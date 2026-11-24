from decimal import Decimal
from app.extensions import db
from app.models import User, Category, FoodItem, Order, OrderItem


def seed_admin_test_env(app):
    """Sets up an administrator account, a customer account, a category, and an order."""
    with app.app_context():
        # Administrator
        admin = User(name='Executive Chef', email='chef@craveadmin.com', role='admin')
        admin.set_password('AdminPass123!')

        # Customer
        customer = User(name='Regular Customer', email='customer@craveuser.com', role='customer')
        customer.set_password('CustomerPass123!')

        cat = Category(name='Artisan Breads', description='Freshly baked sourdoughs')
        db.session.add_all([admin, customer, cat])
        db.session.flush()

        dish = FoodItem(
            name='Garlic Herb Focaccia',
            description='Rosemary sea salt focaccia',
            price=Decimal('6.50'),
            category_id=cat.id,
            is_available=True
        )
        db.session.add(dish)
        db.session.flush()

        order = Order(
            user_id=customer.id,
            customer_name='Regular Customer',
            phone_number='555-0199',
            delivery_address='101 Food Blvd',
            payment_method='Cash on Delivery',
            status=Order.STATUS_PLACED,
            total_amount=Decimal('13.00')
        )
        db.session.add(order)
        db.session.flush()
        order.order_number = order.generate_order_number()

        item = OrderItem(
            order_id=order.id,
            food_item_id=dish.id,
            item_name=dish.name,
            unit_price=dish.price,
            quantity=2,
            subtotal=Decimal('13.00')
        )
        db.session.add(item)
        db.session.commit()

        return admin.id, customer.id, cat.id, dish.id, order.id


def test_customer_cannot_access_admin_dashboard(client, app):
    """Test that customer accounts receive HTTP 403 Forbidden when attempting to access admin routes."""
    seed_admin_test_env(app)

    # Login as Customer
    client.post('/auth/login', data={'email': 'customer@craveuser.com', 'password': 'CustomerPass123!'})

    # Customer tries to access admin routes
    for endpoint in ['/admin/dashboard', '/admin/categories', '/admin/items', '/admin/orders']:
        res = client.get(endpoint)
        assert res.status_code == 403
        assert b'403' in res.data
        assert b'Access Denied' in res.data


def test_anonymous_cannot_access_admin_dashboard(client, app):
    """Test that unauthenticated requests to admin routes are redirected to login."""
    res = client.get('/admin/dashboard')
    assert res.status_code == 302
    assert '/auth/login' in res.headers['Location']


def test_admin_can_access_dashboard_and_stats(client, app):
    """Test that administrator can access the dashboard and view live metrics."""
    seed_admin_test_env(app)

    # Login as Admin
    client.post('/auth/login', data={'email': 'chef@craveadmin.com', 'password': 'AdminPass123!'})

    res = client.get('/admin/dashboard')
    assert res.status_code == 200
    assert b'Operations Dashboard' in res.data
    assert b'Total Orders' in res.data
    assert b'Delivered Revenue' in res.data
    assert b'Active Customers' in res.data
    assert b'Menu Dishes' in res.data


def test_category_crud_operations_and_safe_delete(client, app):
    """Test adding, editing, and safely deleting categories with child dish constraints."""
    _, _, cat_id, dish_id, _ = seed_admin_test_env(app)

    # Login as Admin
    client.post('/auth/login', data={'email': 'chef@craveadmin.com', 'password': 'AdminPass123!'})

    # 1. Add new category
    add_res = client.post('/admin/categories', data={
        'name': 'Decadent Desserts',
        'description': 'Sweet creations'
    }, follow_redirects=True)
    assert add_res.status_code == 200
    assert b'Decadent Desserts' in add_res.data and b'added successfully' in add_res.data

    with app.app_context():
        new_cat = Category.query.filter_by(name='Decadent Desserts').first()
        assert new_cat is not None
        new_cat_id = new_cat.id

    # 2. Edit category
    edit_res = client.post(f'/admin/categories/{new_cat_id}/edit', data={
        'name': 'Gourmet Desserts',
        'description': 'Updated sweet creations'
    }, follow_redirects=True)
    assert edit_res.status_code == 200
    assert b'Gourmet Desserts' in edit_res.data and b'updated successfully' in edit_res.data

    # 3. Safe delete test: try deleting category with attached dishes (cat_id has dish_id attached)
    blocked_delete = client.post(f'/admin/categories/{cat_id}/delete', follow_redirects=True)
    assert b'Cannot delete category' in blocked_delete.data
    assert b'because it still contains' in blocked_delete.data

    # 4. Delete the empty category (new_cat_id has 0 dishes) -> Success
    success_delete = client.post(f'/admin/categories/{new_cat_id}/delete', follow_redirects=True)
    assert b'was successfully deleted' in success_delete.data


def test_food_item_crud_operations_and_price_validation(client, app):
    """Test dish creation, validation, editing, availability toggle, and deletion."""
    _, _, cat_id, dish_id, _ = seed_admin_test_env(app)

    # Login as Admin
    client.post('/auth/login', data={'email': 'chef@craveadmin.com', 'password': 'AdminPass123!'})

    # 1. Reject invalid price (<= 0)
    invalid_price_res = client.post('/admin/items/new', data={
        'name': 'Free Dish',
        'category_id': str(cat_id),
        'price': '0.00',
        'description': 'Should fail',
        'is_available': 'y'
    })
    assert b'Price must be between' in invalid_price_res.data

    # 2. Add new valid dish
    add_dish_res = client.post('/admin/items/new', data={
        'name': 'Rustic Sourdough Loaf',
        'category_id': str(cat_id),
        'price': '8.50',
        'description': '24-hour slow fermented bread',
        'image_url': 'https://example.com/sourdough.jpg',
        'is_available': 'y'
    }, follow_redirects=True)
    assert add_dish_res.status_code == 200
    assert b'Rustic Sourdough Loaf' in add_dish_res.data

    with app.app_context():
        new_dish = FoodItem.query.filter_by(name='Rustic Sourdough Loaf').first()
        assert new_dish is not None
        assert new_dish.price == Decimal('8.50')
        new_dish_id = new_dish.id

    # 3. Quick stock toggle (In Stock -> Out of Stock)
    toggle_res = client.post(f'/admin/items/{new_dish_id}/toggle-stock', follow_redirects=True)
    assert b'is now marked as Out of Stock' in toggle_res.data

    with app.app_context():
        toggled = db.session.get(FoodItem, new_dish_id)
        assert toggled.is_available is False

    # 4. Edit dish
    edit_dish_res = client.post(f'/admin/items/{new_dish_id}/edit', data={
        'name': 'Artisanal Sourdough Loaf (Special Edition)',
        'category_id': str(cat_id),
        'price': '9.50',
        'description': 'Updated recipe',
        'is_available': 'y'
    }, follow_redirects=True)
    assert edit_dish_res.status_code == 200
    assert b'updated successfully' in edit_dish_res.data

    # 5. Delete dish
    del_dish_res = client.post(f'/admin/items/{new_dish_id}/delete', follow_redirects=True)
    assert b'has been removed from the catalog' in del_dish_res.data

    with app.app_context():
        assert db.session.get(FoodItem, new_dish_id) is None


def test_order_filtering_and_search(client, app):
    """Test administrator orders list search and status filtering."""
    _, customer_id, _, _, order1_id = seed_admin_test_env(app)

    with app.app_context():
        # Create second order with DELIVERED status
        order2 = Order(
            user_id=customer_id,
            customer_name='Delivered Customer',
            phone_number='555-9999',
            delivery_address='202 Delivered Way',
            payment_method='Cash on Delivery',
            status=Order.STATUS_DELIVERED,
            total_amount=Decimal('45.00')
        )
        db.session.add(order2)
        db.session.commit()
        order2_id = order2.id

    # Login as Admin
    client.post('/auth/login', data={'email': 'chef@craveadmin.com', 'password': 'AdminPass123!'})

    # 1. Filter by status: PLACED
    placed_filter = client.get('/admin/orders?status=PLACED')
    assert placed_filter.status_code == 200
    assert b'101 Food Blvd' in placed_filter.data
    assert b'202 Delivered Way' not in placed_filter.data

    # 2. Filter by status: DELIVERED
    delivered_filter = client.get('/admin/orders?status=DELIVERED')
    assert delivered_filter.status_code == 200
    assert b'202 Delivered Way' in delivered_filter.data
    assert b'101 Food Blvd' not in delivered_filter.data

    # 3. Search by ID
    search_res = client.get(f'/admin/orders?q={order1_id}')
    assert search_res.status_code == 200
    assert b'101 Food Blvd' in search_res.data
    assert b'202 Delivered Way' not in search_res.data


def test_order_status_valid_and_invalid_transitions(client, app):
    """
    Test transition workflow enforcement:
    PLACED -> CONFIRMED -> PREPARING -> OUT FOR DELIVERY -> DELIVERED
    And test rejection of invalid transitions.
    """
    _, _, _, _, order_id = seed_admin_test_env(app)

    # Login as Admin
    client.post('/auth/login', data={'email': 'chef@craveadmin.com', 'password': 'AdminPass123!'})

    # --- INVALID TRANSITIONS ---
    # 1. PLACED -> DELIVERED (invalid, cannot skip)
    invalid_skip = client.post(f'/admin/orders/{order_id}/status', data={
        'status': 'DELIVERED'
    }, follow_redirects=True)
    assert b'Invalid status transition' in invalid_skip.data

    with app.app_context():
        order = db.session.get(Order, order_id)
        assert order.status == Order.STATUS_PLACED

    # --- VALID TRANSITION PROGRESSION ---
    # 2. PLACED -> CONFIRMED (valid)
    t1 = client.post(f'/admin/orders/{order_id}/status', data={'status': 'CONFIRMED'}, follow_redirects=True)
    assert b'status updated from PLACED to CONFIRMED' in t1.data

    # 3. CONFIRMED -> PREPARING (valid)
    t2 = client.post(f'/admin/orders/{order_id}/status', data={'status': 'PREPARING'}, follow_redirects=True)
    assert b'status updated from CONFIRMED to PREPARING' in t2.data

    # 4. PREPARING -> OUT FOR DELIVERY (valid)
    t3 = client.post(f'/admin/orders/{order_id}/status', data={'status': 'OUT FOR DELIVERY'}, follow_redirects=True)
    assert b'status updated from PREPARING to OUT FOR DELIVERY' in t3.data

    # 5. OUT FOR DELIVERY -> DELIVERED (valid)
    t4 = client.post(f'/admin/orders/{order_id}/status', data={'status': 'DELIVERED'}, follow_redirects=True)
    assert b'status updated from OUT FOR DELIVERY to DELIVERED' in t4.data

    # 6. DELIVERED -> CANCELLED (invalid: terminal state)
    terminal_test = client.post(f'/admin/orders/{order_id}/status', data={'status': 'CANCELLED'}, follow_redirects=True)
    assert b'Invalid status transition' in terminal_test.data

    with app.app_context():
        order = db.session.get(Order, order_id)
        assert order.status == Order.STATUS_DELIVERED
