from decimal import Decimal
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from app.admin import admin_bp
from app.extensions import db
from app.models import User, Category, FoodItem, Order
from app.forms import CategoryForm, FoodItemForm, OrderStatusForm
from app.utils import admin_required


# ==============================================================================
# DASHBOARD OVERVIEW
# ==============================================================================

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """
    Administrative Operations Control Center.
    Presents key operational statistics, financial revenue from delivered orders,
    status breakdown, and recent orders feed.
    """
    total_orders = Order.query.count()
    total_customers = User.query.filter_by(role='customer').count()
    total_food_items = FoodItem.query.count()

    # Revenue strictly from delivered orders
    delivered_orders = Order.query.filter_by(status=Order.STATUS_DELIVERED).all()
    total_revenue = sum((o.total_amount for o in delivered_orders), Decimal('0.00'))

    # Order count breakdown by fulfillment stage
    status_counts = {
        status: Order.query.filter_by(status=status).count()
        for status in Order.ALL_STATUSES
    }

    # Active orders requiring kitchen/dispatch action
    active_orders_count = Order.query.filter(
        Order.status.in_([
            Order.STATUS_PLACED,
            Order.STATUS_CONFIRMED,
            Order.STATUS_PREPARING,
            Order.STATUS_OUT_FOR_DELIVERY
        ])
    ).count()

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()

    return render_template(
        'admin/dashboard.html',
        total_orders=total_orders,
        total_customers=total_customers,
        total_food_items=total_food_items,
        total_revenue=total_revenue,
        status_counts=status_counts,
        active_orders_count=active_orders_count,
        recent_orders=recent_orders
    )


# ==============================================================================
# CATEGORY MANAGEMENT
# ==============================================================================

@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    """Lists all food categories and handles inline new category addition."""
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        existing = Category.query.filter(Category.name.ilike(name)).first()
        if existing:
            flash(f'A category named "{name}" already exists.', 'warning')
        else:
            category = Category(
                name=name,
                description=form.description.data.strip() if form.description.data else None
            )
            db.session.add(category)
            db.session.commit()
            flash(f'Category "{category.name}" added successfully.', 'success')
            return redirect(url_for('admin.categories'))

    all_categories = Category.query.order_by(Category.name.asc()).all()
    return render_template(
        'admin/categories.html',
        categories=all_categories,
        form=form
    )


@admin_bp.route('/categories/<int:cat_id>/edit', methods=['GET', 'POST'])
@admin_required
def category_edit(cat_id: int):
    """Edits an existing food category's metadata."""
    category = db.get_or_404(Category, cat_id)
    form = CategoryForm(obj=category)

    if form.validate_on_submit():
        new_name = form.name.data.strip()
        # Check uniqueness excluding self
        existing = Category.query.filter(Category.name.ilike(new_name), Category.id != cat_id).first()
        if existing:
            flash(f'Another category named "{new_name}" already exists.', 'warning')
        else:
            category.name = new_name
            category.description = form.description.data.strip() if form.description.data else None
            db.session.commit()
            flash(f'Category "{category.name}" updated successfully.', 'success')
            return redirect(url_for('admin.categories'))

    return render_template('admin/category_edit.html', category=category, form=form)


@admin_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@admin_required
def category_delete(cat_id: int):
    """
    Safely deletes an empty food category.
    Strictly prevents deleting categories that still have referenced food items.
    """
    category = db.get_or_404(Category, cat_id)
    referenced_items_count = len(category.food_items)

    if referenced_items_count > 0:
        flash(
            f'Cannot delete category "{category.name}" because it still contains '
            f'{referenced_items_count} dish(es). Please delete or reassign those dishes first.',
            'warning'
        )
        return redirect(url_for('admin.categories'))

    db.session.delete(category)
    db.session.commit()
    flash(f'Category "{category.name}" was successfully deleted.', 'success')
    return redirect(url_for('admin.categories'))


# ==============================================================================
# FOOD ITEM MANAGEMENT
# ==============================================================================

@admin_bp.route('/items')
@admin_required
def items():
    """Lists menu dishes with category filtering, search, and quick availability toggles."""
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

    all_items = query.order_by(FoodItem.category_id.asc(), FoodItem.name.asc()).all()
    categories_list = Category.query.order_by(Category.name.asc()).all()

    return render_template(
        'admin/items.html',
        items=all_items,
        categories=categories_list,
        selected_category_id=selected_category_id,
        search_query=search_query
    )


@admin_bp.route('/items/new', methods=['GET', 'POST'])
@admin_required
def item_create():
    """Creates a new dish and assigns it to a category."""
    form = FoodItemForm()
    # Populate category dropdown options
    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.name.asc()).all()
    ]

    if not form.category_id.choices:
        flash('Please create at least one category before adding food items.', 'warning')
        return redirect(url_for('admin.categories'))

    if form.validate_on_submit():
        dish = FoodItem(
            name=form.name.data.strip(),
            category_id=form.category_id.data,
            price=form.price.data,
            description=form.description.data.strip() if form.description.data else None,
            image_url=form.image_url.data.strip() if form.image_url.data else None,
            is_available=form.is_available.data
        )
        db.session.add(dish)
        db.session.commit()
        flash(f'Dish "{dish.name}" added to menu catalog.', 'success')
        return redirect(url_for('admin.items'))

    return render_template('admin/item_form.html', form=form, title='Add New Dish')


@admin_bp.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
@admin_required
def item_edit(item_id: int):
    """Edits an existing food item."""
    dish = db.get_or_404(FoodItem, item_id)
    form = FoodItemForm(obj=dish)
    form.category_id.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.name.asc()).all()
    ]

    if form.validate_on_submit():
        dish.name = form.name.data.strip()
        dish.category_id = form.category_id.data
        dish.price = form.price.data
        dish.description = form.description.data.strip() if form.description.data else None
        dish.image_url = form.image_url.data.strip() if form.image_url.data else None
        dish.is_available = form.is_available.data

        db.session.commit()
        flash(f'Dish "{dish.name}" updated successfully.', 'success')
        return redirect(url_for('admin.items'))

    return render_template('admin/item_form.html', form=form, title=f'Edit: {dish.name}', dish=dish)


@admin_bp.route('/items/<int:item_id>/toggle-stock', methods=['POST'])
@admin_required
def item_toggle_stock(item_id: int):
    """Quickly toggles dish stock availability between In Stock and Out of Stock."""
    dish = db.get_or_404(FoodItem, item_id)
    dish.is_available = not dish.is_available
    db.session.commit()

    status_label = "In Stock" if dish.is_available else "Out of Stock"
    flash(f'"{dish.name}" is now marked as {status_label}.', 'info')
    return redirect(request.referrer or url_for('admin.items'))


@admin_bp.route('/items/<int:item_id>/delete', methods=['POST'])
@admin_required
def item_delete(item_id: int):
    """
    Deletes a food item from the menu catalog.
    Historical order items safely maintain their snapshot name and price.
    """
    dish = db.get_or_404(FoodItem, item_id)
    dish_name = dish.name
    db.session.delete(dish)
    db.session.commit()

    flash(f'Dish "{dish_name}" has been removed from the catalog.', 'success')
    return redirect(url_for('admin.items'))


# ==============================================================================
# ORDER MANAGEMENT & STATUS FULFILLMENT
# ==============================================================================

@admin_bp.route('/orders')
@admin_required
def orders():
    """
    Orders inspection portal for administrators.
    Supports filtering by fulfillment status and search by Order ID or Order Number.
    """
    status_filter = request.args.get('status', '').strip().upper()
    search_query = request.args.get('q', '').strip()

    query = Order.query

    if status_filter and status_filter in Order.ALL_STATUSES:
        query = query.filter(Order.status == status_filter)

    if search_query:
        # Search by order_number, customer_name, or integer ID
        if search_query.isdigit():
            query = query.filter(
                or_(
                    Order.id == int(search_query),
                    Order.order_number.ilike(f'%{search_query}%'),
                    Order.customer_name.ilike(f'%{search_query}%'),
                    Order.phone_number.ilike(f'%{search_query}%')
                )
            )
        else:
            query = query.filter(
                or_(
                    Order.order_number.ilike(f'%{search_query}%'),
                    Order.customer_name.ilike(f'%{search_query}%'),
                    Order.phone_number.ilike(f'%{search_query}%')
                )
            )

    all_orders = query.order_by(Order.created_at.desc()).all()

    # Calculate status counts for quick tab badges
    status_counts = {
        s: Order.query.filter_by(status=s).count()
        for s in Order.ALL_STATUSES
    }

    return render_template(
        'admin/orders.html',
        orders=all_orders,
        status_filter=status_filter,
        search_query=search_query,
        status_counts=status_counts,
        all_statuses=Order.ALL_STATUSES
    )


@admin_bp.route('/orders/<int:order_id>')
@admin_required
def order_detail(order_id: int):
    """Detailed audit view of an order with customer details, items, and status transition control."""
    order = db.get_or_404(Order, order_id)
    form = OrderStatusForm()
    
    # Configure available target transitions based on current order status
    allowed = order.allowed_transitions()
    form.status.choices = [(s, s) for s in allowed]

    return render_template(
        'admin/order_detail.html',
        order=order,
        form=form,
        allowed_transitions=allowed
    )


@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def order_update_status(order_id: int):
    """
    Enforces valid status transition rules:
    - PLACED -> CONFIRMED or CANCELLED
    - CONFIRMED -> PREPARING or CANCELLED
    - PREPARING -> OUT FOR DELIVERY
    - OUT FOR DELIVERY -> DELIVERED
    Strictly rejects invalid or out-of-order transitions.
    """
    order = db.get_or_404(Order, order_id)
    target_status = request.form.get('status', '').strip().upper()

    # Validate transition against state machine rules
    if not order.can_transition_to(target_status):
        allowed = order.allowed_transitions()
        allowed_str = ", ".join(allowed) if allowed else "None (Terminal State)"
        flash(
            f'Invalid status transition from "{order.status}" to "{target_status}". '
            f'Allowed next statuses: {allowed_str}.',
            'danger'
        )
        return redirect(url_for('admin.order_detail', order_id=order.id))

    # Execute valid transition
    old_status = order.status
    order.status = target_status
    db.session.commit()

    flash(f'Order {order.order_number or order.id} status updated from {old_status} to {target_status}.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order.id))
