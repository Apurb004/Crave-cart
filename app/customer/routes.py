from decimal import Decimal
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_required, current_user
from sqlalchemy import or_
from app.customer import customer_bp
from app.extensions import db
from app.models import Category, FoodItem, Order
from app.forms import CheckoutForm
from app.services import CartService, OrderService


@customer_bp.route('/')
def index():
    """
    Homepage featuring the brand hero banner, restaurant introduction,
    featured culinary dishes, and categories.
    """
    categories = Category.query.order_by(Category.name).all()
    featured_items = FoodItem.query.filter_by(is_available=True).order_by(FoodItem.id.desc()).limit(6).all()
    return render_template(
        'customer/index.html',
        categories=categories,
        featured_items=featured_items
    )


@customer_bp.route('/menu')
def menu():
    """
    Menu catalog page with search functionality, category-based filtering,
    and responsive food cards.
    """
    categories = Category.query.order_by(Category.name).all()
    selected_category_id = request.args.get('category', type=int)
    search_query = request.args.get('q', '').strip()

    query = FoodItem.query

    if selected_category_id:
        query = query.filter(FoodItem.category_id == selected_category_id)

    if search_query:
        query = query.filter(
            or_(
                FoodItem.name.ilike(f'%{search_query}%'),
                FoodItem.description.ilike(f'%{search_query}%')
            )
        )

    items = query.order_by(FoodItem.is_available.desc(), FoodItem.name.asc()).all()

    return render_template(
        'customer/menu.html',
        categories=categories,
        items=items,
        selected_category_id=selected_category_id,
        search_query=search_query
    )


@customer_bp.route('/food/<int:item_id>')
def food_detail(item_id: int):
    """
    Detailed food page displaying presentation,
    culinary description, and Add-to-Cart controls.
    """
    item = db.get_or_404(FoodItem, item_id)
    related_items = FoodItem.query.filter(
        FoodItem.category_id == item.category_id,
        FoodItem.id != item.id,
        FoodItem.is_available.is_(True)
    ).limit(3).all()

    return render_template(
        'customer/food_detail.html',
        item=item,
        related_items=related_items
    )


# ==============================================================================
# SHOPPING CART ENDPOINTS
# ==============================================================================

@customer_bp.route('/cart')
def view_cart():
    """
    Shopping cart review view.
    Recalculates all prices, quantities, and availability server-side.
    """
    session_cart = session.setdefault('cart', {})
    cart_details = CartService.get_cart_details(session_cart)

    return render_template(
        'customer/cart.html',
        cart_items=cart_details['items'],
        total_amount=cart_details['total_amount'],
        total_quantity=cart_details['total_quantity'],
        has_unavailable=cart_details['has_unavailable'],
        unavailable_items=cart_details['unavailable_items']
    )


@customer_bp.route('/cart/add/<int:item_id>', methods=['POST'])
def add_to_cart(item_id: int):
    """Adds a dish to the session shopping cart with availability check."""
    session_cart = session.setdefault('cart', {})

    try:
        quantity = int(request.form.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    success, message = CartService.add_item(session_cart, item_id, quantity)
    session.modified = True

    flash(message, 'success' if success else 'warning')
    return redirect(request.referrer or url_for('customer.menu'))


@customer_bp.route('/cart/update/<int:item_id>', methods=['POST'])
def update_cart_item(item_id: int):
    """
    Increases, decreases, or modifies item quantity in cart.
    Accepts 'delta' (+1 / -1) or 'action' ('increase' / 'decrease').
    """
    session_cart = session.setdefault('cart', {})
    
    action = request.form.get('action')
    delta = 0
    if action == 'increase':
        delta = 1
    elif action == 'decrease':
        delta = -1
    else:
        try:
            delta = int(request.form.get('delta', 0))
        except (ValueError, TypeError):
            delta = 0

    success, message = CartService.update_quantity(session_cart, item_id, delta=delta)
    session.modified = True

    flash(message, 'info' if success else 'warning')
    return redirect(url_for('customer.view_cart'))


@customer_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
def remove_cart_item(item_id: int):
    """Removes a single item from the session shopping cart."""
    session_cart = session.setdefault('cart', {})
    success, message = CartService.remove_item(session_cart, item_id)
    session.modified = True

    flash(message, 'info' if success else 'warning')
    return redirect(url_for('customer.view_cart'))


@customer_bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    """Empties all items from the session shopping cart."""
    session_cart = session.setdefault('cart', {})
    CartService.clear_cart(session_cart)
    session.modified = True

    flash('Your shopping cart has been cleared.', 'info')
    return redirect(url_for('customer.view_cart'))


# ==============================================================================
# CHECKOUT & ORDER PROCESSING
# ==============================================================================

@customer_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """
    Customer checkout view. Validates cart server-side, captures delivery
    coordinates, and processes Cash on Delivery order creation.
    """
    session_cart = session.setdefault('cart', {})
    cart_details = CartService.get_cart_details(session_cart)

    # Empty cart cannot proceed to checkout
    if not cart_details['items']:
        flash('Your shopping cart is empty. Please add items before checking out.', 'warning')
        return redirect(url_for('customer.menu'))

    # Block checkout if any item in cart is unavailable
    if cart_details['has_unavailable']:
        flash('One or more items in your cart are currently sold out. Please remove them before placing your order.', 'warning')
        return redirect(url_for('customer.view_cart'))

    form = CheckoutForm()

    # Pre-populate recipient name with customer's registered account name on GET
    if request.method == 'GET' and not form.customer_name.data:
        form.customer_name.data = current_user.name

    if form.validate_on_submit():
        success, order, message = OrderService.create_order(
            user_id=current_user.id,
            customer_name=form.customer_name.data,
            phone_number=form.phone_number.data,
            delivery_address=form.delivery_address.data,
            session_cart=session_cart,
            order_notes=form.order_notes.data
        )

        if success:
            session.modified = True
            flash('Your order has been received by our kitchen! Thank you for ordering with CraveCart.', 'success')
            return redirect(url_for('customer.order_confirmation', order_id=order.id))
        else:
            flash(message, 'danger')

    return render_template(
        'customer/checkout.html',
        form=form,
        cart_items=cart_details['items'],
        total_amount=cart_details['total_amount'],
        total_quantity=cart_details['total_quantity']
    )


@customer_bp.route('/orders/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id: int):
    """Displays order receipt and tracking summary immediately post-checkout."""
    order = db.get_or_404(Order, order_id)

    # Authorization guard: customers can only access their own orders
    if order.user_id != current_user.id:
        abort(403)

    return render_template('customer/order_confirmation.html', order=order)


# ==============================================================================
# ORDER HISTORY & TRACKING
# ==============================================================================

@customer_bp.route('/orders')
@login_required
def order_history():
    """Lists past and active orders for the currently authenticated customer."""
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('customer/orders.html', orders=orders)


@customer_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id: int):
    """
    Detailed audit view of an individual order, including immutable receipt,
    delivery coordinates, and progressive visual status timeline.
    """
    order = db.get_or_404(Order, order_id)

    # Authorization guard
    if order.user_id != current_user.id:
        abort(403)

    # Define the linear status stages for the timeline
    stages = [
        Order.STATUS_PLACED,
        Order.STATUS_CONFIRMED,
        Order.STATUS_PREPARING,
        Order.STATUS_OUT_FOR_DELIVERY,
        Order.STATUS_DELIVERED
    ]

    return render_template(
        'customer/order_detail.html',
        order=order,
        stages=stages
    )


@customer_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id: int):
    """
    Customer self-service order cancellation.
    Permitted only while the order remains in PLACED status.
    """
    success, message = OrderService.cancel_order(order_id, current_user.id)
    flash(message, 'info' if success else 'warning')
    return redirect(url_for('customer.order_detail', order_id=order_id))
