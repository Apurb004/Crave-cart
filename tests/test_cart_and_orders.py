from decimal import Decimal
from app.extensions import db
from app.models import User, Category, FoodItem, Order, OrderItem
from app.services import CartService, OrderService


def seed_cart_test_environment(app):
    """Sets up customer, category, in-stock dish, and out-of-stock dish."""
    with app.app_context():
        # Customer 1
        user1 = User(name='Alice Customer', email='alice@crave.com', role='customer')
        user1.set_password('AlicePass123!')
        
        # Customer 2
        user2 = User(name='Bob Customer', email='bob@crave.com', role='customer')
        user2.set_password('BobPass123!')

        cat = Category(name='Gourmet Mains', description='Artisanal mains')
        db.session.add_all([user1, user2, cat])
        db.session.flush()

        dish1 = FoodItem(
            name='Handmade Tagliatelle',
            description='Fresh pasta with slow-cooked ragu',
            price=Decimal('18.00'),
            category_id=cat.id,
            is_available=True
        )
        dish2 = FoodItem(
            name='Truffle Risotto',
            description='Creamy arborio rice with black truffle',
            price=Decimal('22.50'),
            category_id=cat.id,
            is_available=True
        )
        dish3 = FoodItem(
            name='Rare Wagyu Steak',
            description='A5 Wagyu pan seared',
            price=Decimal('65.00'),
            category_id=cat.id,
            is_available=False  # Out of stock
        )
        db.session.add_all([dish1, dish2, dish3])
        db.session.commit()

        return user1.id, user2.id, dish1.id, dish2.id, dish3.id


def test_cart_operations_add_increase_decrease_remove_clear(client, app):
    """Test comprehensive cart lifecycle: add, +qty, -qty, remove item, clear cart."""
    _, _, dish1_id, dish2_id, _ = seed_cart_test_environment(app)

    # 1. Add Dish 1 (qty 1)
    res = client.post(f'/cart/add/{dish1_id}', data={'quantity': '1'}, follow_redirects=True)
    assert res.status_code == 200
    assert b'Handmade Tagliatelle' in res.data
    assert b'id="cartBadgeCount">1</span>' in res.data

    # 2. Add Dish 2 (qty 2)
    client.post(f'/cart/add/{dish2_id}', data={'quantity': '2'}, follow_redirects=True)
    cart_res = client.get('/cart')
    assert b'Handmade Tagliatelle' in cart_res.data
    assert b'Truffle Risotto' in cart_res.data
    assert b'id="cartBadgeCount">3</span>' in cart_res.data
    # Total: 18.00 + (22.50 * 2) = 63.00
    assert b'63.00' in cart_res.data

    # 3. Increase quantity of Dish 1
    client.post(f'/cart/update/{dish1_id}', data={'action': 'increase'}, follow_redirects=True)
    cart_res2 = client.get('/cart')
    assert b'id="cartBadgeCount">4</span>' in cart_res2.data
    # Total: (18.00 * 2) + (22.50 * 2) = 81.00
    assert b'81.00' in cart_res2.data

    # 4. Decrease quantity of Dish 2
    client.post(f'/cart/update/{dish2_id}', data={'action': 'decrease'}, follow_redirects=True)
    cart_res3 = client.get('/cart')
    assert b'id="cartBadgeCount">3</span>' in cart_res3.data
    # Total: (18.00 * 2) + 22.50 = 58.50
    assert b'58.50' in cart_res3.data

    # 5. Remove Dish 1
    remove_res = client.post(f'/cart/remove/{dish1_id}', follow_redirects=True)
    assert b'Removed' in remove_res.data
    assert b'Handmade Tagliatelle' in remove_res.data
    assert b'id="cartBadgeCount">1</span>' in remove_res.data

    # 6. Clear entire cart
    client.post('/cart/clear', follow_redirects=True)
    empty_cart = client.get('/cart')
    assert b'Your cart is currently empty' in empty_cart.data
    assert b'id="cartBadgeCount">0</span>' in empty_cart.data


def test_cart_quantity_validation_and_stock_restriction(client, app):
    """Test stock enforcement and boundary limits on quantity."""
    _, _, dish1_id, _, dish3_soldout = seed_cart_test_environment(app)

    # Adding sold out dish should be blocked
    res = client.post(f'/cart/add/{dish3_soldout}', data={'quantity': '1'}, follow_redirects=True)
    assert b'is currently sold out' in res.data
    cart_res = client.get('/cart')
    assert b'Rare Wagyu Steak' not in cart_res.data

    # Decreasing quantity to 0 removes the item
    client.post(f'/cart/add/{dish1_id}', data={'quantity': '1'}, follow_redirects=True)
    dec_res = client.post(f'/cart/update/{dish1_id}', data={'action': 'decrease'}, follow_redirects=True)
    assert b'Removed' in dec_res.data
    assert b'Handmade Tagliatelle' in dec_res.data
    assert b'Your cart is currently empty' in dec_res.data


def test_cart_price_calculation_integrity(app):
    """Test that all prices and subtotals are calculated strictly on the server."""
    _, _, dish1_id, dish2_id, _ = seed_cart_test_environment(app)

    with app.app_context():
        # Simulate session cart
        session_cart = {str(dish1_id): 3, str(dish2_id): 2}
        details = CartService.get_cart_details(session_cart)

        # Expected: (18.00 * 3) + (22.50 * 2) = 54.00 + 45.00 = 99.00
        assert details['total_quantity'] == 5
        assert details['total_amount'] == Decimal('99.00')
        assert len(details['items']) == 2
        assert details['has_unavailable'] is False


def test_checkout_validation(client, app):
    """Test checkout authorization, empty cart prevention, and form validation."""
    user1_id, _, dish1_id, _, _ = seed_cart_test_environment(app)

    # 1. Anonymous checkout redirects to login
    anon_res = client.get('/checkout')
    assert anon_res.status_code == 302
    assert '/auth/login' in anon_res.headers['Location']

    # Login as Alice
    client.post('/auth/login', data={'email': 'alice@crave.com', 'password': 'AlicePass123!'})

    # 2. Checkout with empty cart redirects to menu
    empty_res = client.get('/checkout', follow_redirects=True)
    assert b'Your shopping cart is empty' in empty_res.data

    # 3. Add item and visit checkout
    client.post(f'/cart/add/{dish1_id}', data={'quantity': '2'})
    checkout_page = client.get('/checkout')
    assert checkout_page.status_code == 200
    assert b'Delivery Information' in checkout_page.data
    assert b'Cash on Delivery' in checkout_page.data

    # 4. Submit invalid form (missing phone & short address)
    invalid_post = client.post('/checkout', data={
        'customer_name': 'A',  # Too short
        'phone_number': '',
        'delivery_address': 'Short',
        'order_notes': ''
    })
    assert b'Name must be between 2 and 100 characters' in invalid_post.data
    assert b'Please provide a contact phone number' in invalid_post.data


def test_order_creation_and_cart_clearing(client, app):
    """Test atomic order placement, snapshot storage, total calculation, and cart clearing."""
    user1_id, _, dish1_id, dish2_id, _ = seed_cart_test_environment(app)

    # Login as Alice
    client.post('/auth/login', data={'email': 'alice@crave.com', 'password': 'AlicePass123!'})

    # Add items to cart
    client.post(f'/cart/add/{dish1_id}', data={'quantity': '1'})
    client.post(f'/cart/add/{dish2_id}', data={'quantity': '2'})

    # Place order
    response = client.post('/checkout', data={
        'customer_name': 'Alice Recipient',
        'phone_number': '+1 555-0199',
        'delivery_address': '742 Evergreen Terrace, Food City',
        'order_notes': 'Please ring the doorbell.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Thank You for Your Order!' in response.data
    assert b'Alice Recipient' in response.data
    assert b'Cash on Delivery' in response.data

    # Cart must be emptied after successful placement
    assert b'id="cartBadgeCount">0</span>' in response.data

    with app.app_context():
        order = Order.query.filter_by(user_id=user1_id).first()
        assert order is not None
        assert order.customer_name == 'Alice Recipient'
        assert order.status == Order.STATUS_PLACED
        assert order.payment_method == 'Cash on Delivery'
        # Total: 18.00 + (22.50 * 2) = 63.00
        assert order.total_amount == Decimal('63.00')
        assert len(order.items) == 2

        # Verify historical price snapshot
        item1 = next(i for i in order.items if i.food_item_id == dish1_id)
        assert item1.item_name == 'Handmade Tagliatelle'
        assert item1.unit_price == Decimal('18.00')
        assert item1.quantity == 1
        assert item1.subtotal == Decimal('18.00')


def test_order_history_and_customer_authorization(client, app):
    """Test customer order history and verify that customer A cannot access customer B's order."""
    user1_id, user2_id, dish1_id, _, _ = seed_cart_test_environment(app)

    # Create Order for Alice (User 1)
    with app.app_context():
        order_alice = Order(
            user_id=user1_id,
            customer_name='Alice Customer',
            phone_number='555-1111',
            delivery_address='123 Alice St',
            total_amount=Decimal('18.00'),
            status=Order.STATUS_PLACED
        )
        db.session.add(order_alice)
        db.session.commit()
        alice_order_id = order_alice.id

        # Create Order for Bob (User 2)
        order_bob = Order(
            user_id=user2_id,
            customer_name='Bob Customer',
            phone_number='555-2222',
            delivery_address='456 Bob Ave',
            total_amount=Decimal('36.00'),
            status=Order.STATUS_CONFIRMED
        )
        db.session.add(order_bob)
        db.session.commit()
        bob_order_id = order_bob.id

    # 1. Login as Alice
    client.post('/auth/login', data={'email': 'alice@crave.com', 'password': 'AlicePass123!'})

    # Alice views her order history
    history_res = client.get('/orders')
    assert history_res.status_code == 200
    assert b'123 Alice St' in history_res.data
    assert b'456 Bob Ave' not in history_res.data  # Cannot see Bob's address

    # Alice can view her own order details
    alice_detail = client.get(f'/orders/{alice_order_id}')
    assert alice_detail.status_code == 200
    assert b'123 Alice St' in alice_detail.data

    # Alice attempts to view Bob's order -> 403 Forbidden!
    unauth_detail = client.get(f'/orders/{bob_order_id}')
    assert unauth_detail.status_code == 403


def test_order_cancellation_rules(client, app):
    """Test that customer can cancel PLACED orders, but not CONFIRMED/PREPARING/DELIVERED."""
    user1_id, _, _, _, _ = seed_cart_test_environment(app)

    with app.app_context():
        order_placed = Order(
            user_id=user1_id,
            customer_name='Alice',
            phone_number='555-1111',
            delivery_address='123 St',
            total_amount=Decimal('20.00'),
            status=Order.STATUS_PLACED
        )
        order_confirmed = Order(
            user_id=user1_id,
            customer_name='Alice',
            phone_number='555-1111',
            delivery_address='123 St',
            total_amount=Decimal('20.00'),
            status=Order.STATUS_CONFIRMED
        )
        db.session.add_all([order_placed, order_confirmed])
        db.session.commit()
        placed_id = order_placed.id
        confirmed_id = order_confirmed.id

    # Login as Alice
    client.post('/auth/login', data={'email': 'alice@crave.com', 'password': 'AlicePass123!'})

    # 1. Cancel PLACED order -> Success
    cancel_res = client.post(f'/orders/{placed_id}/cancel', follow_redirects=True)
    assert cancel_res.status_code == 200
    assert b'Your order has been successfully cancelled' in cancel_res.data

    with app.app_context():
        reloaded = db.session.get(Order, placed_id)
        assert reloaded.status == Order.STATUS_CANCELLED

    # 2. Cancel CONFIRMED order -> Blocked
    cancel_confirmed_res = client.post(f'/orders/{confirmed_id}/cancel', follow_redirects=True)
    assert b'Cannot cancel order' in cancel_confirmed_res.data

    with app.app_context():
        reloaded_confirmed = db.session.get(Order, confirmed_id)
        assert reloaded_confirmed.status == Order.STATUS_CONFIRMED
