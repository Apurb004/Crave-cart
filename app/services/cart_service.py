from decimal import Decimal
from app.extensions import db
from app.models import FoodItem


class CartService:
    """
    Business logic service for session-based shopping cart.
    All calculations strictly use server-side database records.
    Prices or totals submitted from client browsers are never trusted.
    """

    @staticmethod
    def get_cart_details(session_cart: dict) -> dict:
        """
        Reconciles the raw session cart against the database.
        Calculates line item subtotals and grand total with Decimal precision.
        Identifies any unavailable or restocked dishes.
        """
        if not session_cart or not isinstance(session_cart, dict):
            return {
                'items': [],
                'total_amount': Decimal('0.00'),
                'total_quantity': 0,
                'has_unavailable': False,
                'unavailable_items': []
            }

        # Parse integer IDs from session dictionary keys
        valid_ids = []
        clean_quantities = {}
        for k, v in session_cart.items():
            try:
                item_id = int(k)
                qty = int(v)
                if qty > 0:
                    valid_ids.append(item_id)
                    clean_quantities[item_id] = min(qty, 50)
            except (ValueError, TypeError):
                continue

        if not valid_ids:
            return {
                'items': [],
                'total_amount': Decimal('0.00'),
                'total_quantity': 0,
                'has_unavailable': False,
                'unavailable_items': []
            }

        # Fetch all referenced food items from SQLite in a single query
        food_items = FoodItem.query.filter(FoodItem.id.in_(valid_ids)).all()
        food_map = {f.id: f for f in food_items}

        cart_items = []
        total_amount = Decimal('0.00')
        total_quantity = 0
        has_unavailable = False
        unavailable_items = []

        for item_id in valid_ids:
            if item_id in food_map:
                food = food_map[item_id]
                qty = clean_quantities[item_id]

                # Server-calculated line subtotal using database price
                subtotal = (Decimal(str(food.price)) * qty).quantize(Decimal('0.01'))
                
                if food.is_available:
                    total_amount += subtotal
                else:
                    has_unavailable = True
                    unavailable_items.append(food)

                total_quantity += qty
                cart_items.append({
                    'item': food,
                    'item_id': food.id,
                    'quantity': qty,
                    'unit_price': food.price,
                    'subtotal': subtotal,
                    'is_available': food.is_available
                })

        return {
            'items': cart_items,
            'total_amount': total_amount.quantize(Decimal('0.01')),
            'total_quantity': total_quantity,
            'has_unavailable': has_unavailable,
            'unavailable_items': unavailable_items
        }

    @staticmethod
    def add_item(session_cart: dict, item_id: int, quantity: int = 1) -> tuple:
        """
        Adds a food item to the cart or increments existing count.
        Validates stock status against database before allowing addition.
        """
        food = db.session.get(FoodItem, item_id)
        if not food:
            return False, "Selected food item does not exist."

        if not food.is_available:
            return False, f'Sorry, "{food.name}" is currently sold out.'

        if quantity < 1:
            quantity = 1
        elif quantity > 20:
            quantity = 20

        key = str(item_id)
        current_qty = session_cart.get(key, 0)
        session_cart[key] = min(current_qty + quantity, 50)

        return True, f'Added {quantity}x "{food.name}" to your cart.'

    @staticmethod
    def update_quantity(session_cart: dict, item_id: int, delta: int = 0, exact_qty: int = None) -> tuple:
        """
        Increases, decreases, or sets exact quantity for a cart line item.
        Removes item if resulting count drops to 0 or below.
        """
        key = str(item_id)
        if key not in session_cart:
            return False, "Item is not in your cart."

        food = db.session.get(FoodItem, item_id)
        name = food.name if food else "Item"

        if exact_qty is not None:
            if exact_qty <= 0:
                del session_cart[key]
                return True, f'Removed "{name}" from your cart.'
            session_cart[key] = min(exact_qty, 50)
            return True, f'Updated quantity for "{name}".'

        new_qty = session_cart[key] + delta
        if new_qty <= 0:
            del session_cart[key]
            return True, f'Removed "{name}" from your cart.'
        elif new_qty > 50:
            session_cart[key] = 50
            return True, f'Maximum order limit reached (50) for "{name}".'
        else:
            session_cart[key] = new_qty
            action = "Increased" if delta > 0 else "Decreased"
            return True, f'{action} quantity for "{name}".'

    @staticmethod
    def remove_item(session_cart: dict, item_id: int) -> tuple:
        """Removes a specific food item from the cart."""
        key = str(item_id)
        if key in session_cart:
            food = db.session.get(FoodItem, item_id)
            name = food.name if food else "Item"
            del session_cart[key]
            return True, f'Removed "{name}" from your cart.'
        return False, "Item was not found in your cart."

    @staticmethod
    def clear_cart(session_cart: dict) -> None:
        """Empties all items from the session cart."""
        session_cart.clear()
