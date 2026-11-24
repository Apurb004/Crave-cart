from decimal import Decimal
import pytest
from app.extensions import db
from app.models import User, Category, FoodItem, Order


def test_complete_customer_to_admin_e2e_journey(client, app):
    """
    End-to-End Functional Test of the complete 14-step journey:
    1. Customer opens homepage.
    2. Customer browses food.
    3. Customer registers.
    4. Customer logs in.
    5. Customer searches food.
    6. Customer adds items to cart.
    7. Customer updates quantities.
    8. Customer checks out.
    9. Customer places an order.
    10. Customer views order history.
    11. Administrator logs in.
    12. Administrator views the order.
    13. Administrator updates its status.
    14. Customer sees the updated status.
    """

    # --- Setup database with Admin and Food Catalog ---
    with app.app_context():
        # Create Admin
        admin = User(name='Executive Chef', email='admin@cravecart.com', role='admin')
        admin.set_password('AdminMaster2026!')
        db.session.add(admin)

        # Create Category & Dishes
        cat = Category(name='Artisan Pasta', description='Fresh extruded handcrafted pasta')
        db.session.add(cat)
        db.session.flush()

        dish1 = FoodItem(
            name='Truffle Tagliatelle',
            description='Housemade ribbon pasta with black truffle cream and aged parmesan',
            price=Decimal('18.50'),
            category_id=cat.id,
            is_available=True
        )
        dish2 = FoodItem(
            name='Classic Pomodoro',
            description='San Marzano tomato ragu with sweet basil and extra virgin olive oil',
            price=Decimal('12.00'),
            category_id=cat.id,
            is_available=True
        )
        db.session.add_all([dish1, dish2])
        db.session.commit()

        dish1_id = dish1.id
        dish2_id = dish2.id

    # -------------------------------------------------------------
    # 1. Customer opens homepage
    # -------------------------------------------------------------
    home_res = client.get('/')
    assert home_res.status_code == 200
    assert b'CraveCart' in home_res.data
    assert b'Explore Full Menu' in home_res.data
    assert b'Artisanal Kitchen' in home_res.data

    # -------------------------------------------------------------
    # 2. Customer browses food
    # -------------------------------------------------------------
    menu_res = client.get('/menu')
    assert menu_res.status_code == 200
    assert b'Truffle Tagliatelle' in menu_res.data
    assert b'Classic Pomodoro' in menu_res.data

    # -------------------------------------------------------------
    # 3. Customer registers
    # -------------------------------------------------------------
    register_res = client.post('/auth/register', data={
        'name': 'Gourmet Patron',
        'email': 'patron@example.com',
        'password': 'Password123!',
        'confirm_password': 'Password123!'
    }, follow_redirects=True)
    assert register_res.status_code == 200
    assert b'account has been created successfully' in register_res.data

    with app.app_context():
        customer_user = User.query.filter_by(email='patron@example.com').first()
        assert customer_user is not None
        assert customer_user.role == 'customer'

    # -------------------------------------------------------------
    # 4. Customer logs in
    # -------------------------------------------------------------
    login_res = client.post('/auth/login', data={
        'email': 'patron@example.com',
        'password': 'Password123!'
    }, follow_redirects=True)
    assert login_res.status_code == 200
    assert b'Welcome back, Gourmet Patron' in login_res.data
    assert b'My Orders' in login_res.data

    # -------------------------------------------------------------
    # 5. Customer searches food
    # -------------------------------------------------------------
    search_res = client.get('/menu?q=Truffle')
    assert search_res.status_code == 200
    assert b'Truffle Tagliatelle' in search_res.data
    assert b'Classic Pomodoro' not in search_res.data

    # -------------------------------------------------------------
    # 6. Customer adds items to cart
    # -------------------------------------------------------------
    add_res = client.post(f'/cart/add/{dish1_id}', data={'quantity': '1'}, follow_redirects=True)
    assert add_res.status_code == 200
    assert b'Truffle Tagliatelle' in add_res.data
    assert b'to your cart' in add_res.data

    # -------------------------------------------------------------
    # 7. Customer updates quantities
    # -------------------------------------------------------------
    update_res = client.post(f'/cart/update/{dish1_id}', data={'action': 'increase'}, follow_redirects=True)
    assert update_res.status_code == 200
    # 2 items * $18.50 = $37.00
    assert b'$37.00' in update_res.data

    # -------------------------------------------------------------
    # 8. Customer checks out
    # -------------------------------------------------------------
    checkout_page_res = client.get('/checkout')
    assert checkout_page_res.status_code == 200
    assert b'Delivery Information' in checkout_page_res.data
    assert b'Cash on Delivery' in checkout_page_res.data
    assert b'$37.00' in checkout_page_res.data

    # -------------------------------------------------------------
    # 9. Customer places an order
    # -------------------------------------------------------------
    order_place_res = client.post('/checkout', data={
        'customer_name': 'Gourmet Patron',
        'phone_number': '+1-555-0199',
        'delivery_address': '742 Evergreen Terrace, Culinary District, Floor 3',
        'order_notes': 'Please ring the buzzer for Apt 3B'
    }, follow_redirects=True)
    assert order_place_res.status_code == 200
    assert b'Thank You for Your Order!' in order_place_res.data
    assert b'Order Status: PLACED' in order_place_res.data
    assert b'$37.00' in order_place_res.data

    # Verify order in DB and cart cleared
    with app.app_context():
        placed_order = Order.query.filter_by(phone_number='+1-555-0199').first()
        assert placed_order is not None
        assert placed_order.status == 'PLACED'
        assert placed_order.total_amount == Decimal('37.00')
        assert len(placed_order.items) == 1
        assert placed_order.items[0].quantity == 2
        order_id = placed_order.id

    # Verify cart is now empty
    cart_check_res = client.get('/cart')
    assert b'Your cart is currently empty' in cart_check_res.data

    # -------------------------------------------------------------
    # 10. Customer views order history
    # -------------------------------------------------------------
    history_res = client.get('/orders')
    assert history_res.status_code == 200
    assert b'Your Order History' in history_res.data
    assert b'$37.00' in history_res.data

    detail_res = client.get(f'/orders/{order_id}')
    assert detail_res.status_code == 200
    assert b'Placed' in detail_res.data
    assert b'Live Order Progress' in detail_res.data
    assert b'Awaiting kitchen acknowledgment' in detail_res.data

    # -------------------------------------------------------------
    # 11. Administrator logs in
    # -------------------------------------------------------------
    # Customer logs out
    client.post('/auth/logout', follow_redirects=True)

    # Admin logs in
    admin_login_res = client.post('/auth/login', data={
        'email': 'admin@cravecart.com',
        'password': 'AdminMaster2026!'
    }, follow_redirects=True)
    assert admin_login_res.status_code == 200
    assert b'Operations Dashboard' in admin_login_res.data

    # -------------------------------------------------------------
    # 12. Administrator views the order
    # -------------------------------------------------------------
    admin_orders_res = client.get('/admin/orders')
    assert admin_orders_res.status_code == 200
    assert b'Gourmet Patron' in admin_orders_res.data
    assert b'+1-555-0199' in admin_orders_res.data
    assert b'$37.00' in admin_orders_res.data

    admin_order_inspect = client.get(f'/admin/orders/{order_id}')
    assert admin_order_inspect.status_code == 200
    assert b'Order Inspection &amp; Status Transition' in admin_order_inspect.data
    assert b'Advance to: CONFIRMED' in admin_order_inspect.data
    assert b'Please ring the buzzer for Apt 3B' in admin_order_inspect.data

    # -------------------------------------------------------------
    # 13. Administrator updates its status
    # -------------------------------------------------------------
    update_status_res = client.post(f'/admin/orders/{order_id}/status', data={
        'status': 'CONFIRMED'
    }, follow_redirects=True)
    assert update_status_res.status_code == 200
    assert b'status updated from PLACED to CONFIRMED' in update_status_res.data

    with app.app_context():
        refreshed_order = db.session.get(Order, order_id)
        assert refreshed_order.status == 'CONFIRMED'

    # -------------------------------------------------------------
    # 14. Customer sees the updated status
    # -------------------------------------------------------------
    # Admin logs out
    client.post('/auth/logout', follow_redirects=True)

    # Customer logs back in
    client.post('/auth/login', data={
        'email': 'patron@example.com',
        'password': 'Password123!'
    }, follow_redirects=True)

    # Customer inspects their order details
    customer_updated_view = client.get(f'/orders/{order_id}')
    assert customer_updated_view.status_code == 200
    assert b'Confirmed' in customer_updated_view.data
    assert b'Kitchen team has accepted your dining order' in customer_updated_view.data
    # Customer should no longer see the Cancel button because status is CONFIRMED
    assert b'Cancel This Order' not in customer_updated_view.data
