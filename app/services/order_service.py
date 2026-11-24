from decimal import Decimal
from app.extensions import db
from app.models import Order, OrderItem
from app.services.cart_service import CartService


class OrderService:
    """
    Business logic service for atomic checkout, order item snapshot generation,
    financial verification, and status transitions.
    """

    @staticmethod
    def create_order(
        user_id: int,
        customer_name: str,
        phone_number: str,
        delivery_address: str,
        session_cart: dict,
        order_notes: str = None
    ) -> tuple:
        """
        Atomically creates an Order and associated OrderItem records.
        Strictly recalculates prices from database FoodItem records.
        Preserves immutable snapshots of item names and unit prices.
        Clears cart only after successful database commit.
        """
        # Validate cart existence
        cart_details = CartService.get_cart_details(session_cart)
        if not cart_details['items']:
            return False, None, "Your shopping cart is empty."

        # Reject checkout if any item is currently out of stock
        if cart_details['has_unavailable']:
            unavailable_names = ", ".join(f'"{i.name}"' for i in cart_details['unavailable_items'])
            return False, None, f"Order cannot be placed. The following items are sold out: {unavailable_names}."

        if cart_details['total_amount'] <= Decimal('0.00'):
            return False, None, "Invalid order total amount."

        try:
            # 1. Instantiate Order header
            order = Order(
                user_id=user_id,
                customer_name=customer_name.strip(),
                phone_number=phone_number.strip(),
                delivery_address=delivery_address.strip(),
                payment_method='Cash on Delivery',
                status=Order.STATUS_PLACED,
                order_notes=order_notes.strip() if order_notes else None,
                total_amount=Decimal('0.00')
            )
            db.session.add(order)
            db.session.flush()  # Generate primary key ID for foreign key assignment

            # 2. Generate unique human-readable tracking number
            order.order_number = order.generate_order_number()

            # 3. Create immutable line item snapshots
            for entry in cart_details['items']:
                food = entry['item']
                qty = entry['quantity']
                unit_price = Decimal(str(food.price))
                line_subtotal = (unit_price * qty).quantize(Decimal('0.01'))

                order_item = OrderItem(
                    order_id=order.id,
                    food_item_id=food.id,
                    item_name=food.name,
                    unit_price=unit_price,
                    quantity=qty,
                    subtotal=line_subtotal
                )
                db.session.add(order_item)

            # 4. Final verification and total recalculation
            order.recalculate_total()

            # 5. Commit database transaction
            db.session.commit()

            # 6. Clear session cart after successful order creation
            CartService.clear_cart(session_cart)

            return True, order, "Order placed successfully!"

        except Exception as exc:
            db.session.rollback()
            return False, None, f"An unexpected error occurred while placing your order: {str(exc)}"

    @staticmethod
    def cancel_order(order_id: int, user_id: int) -> tuple:
        """
        Cancels an order if placed by the customer and currently in PLACED status.
        Unauthorized or out-of-bounds transitions are strictly rejected.
        """
        order = db.session.get(Order, order_id)
        if not order:
            return False, "Order not found."

        # Security check: Ensure order belongs to the authenticated customer
        if order.user_id != user_id:
            return False, "You do not have permission to modify this order."

        # Business rule: Only PLACED orders can be cancelled by the customer
        if not order.can_cancel:
            return False, f"Cannot cancel order. Orders in '{order.status}' status can no longer be cancelled."

        try:
            order.status = Order.STATUS_CANCELLED
            db.session.commit()
            return True, "Your order has been successfully cancelled."
        except Exception as exc:
            db.session.rollback()
            return False, f"Failed to cancel order: {str(exc)}"
