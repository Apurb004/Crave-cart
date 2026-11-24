from decimal import Decimal
from app.extensions import db
from app.models import User, Category, FoodItem


def seed_test_dishes(app):
    """Helper to populate test categories and dishes."""
    with app.app_context():
        starters = Category(name='Starters', description='Crispy appetizers')
        mains = Category(name='Main Course', description='Hearty entrees')
        db.session.add_all([starters, mains])
        db.session.flush()

        dish1 = FoodItem(
            name='Truffle Fries',
            description='Crispy russet fries with truffle oil',
            price=Decimal('8.50'),
            category_id=starters.id,
            is_available=True
        )
        dish2 = FoodItem(
            name='Spicy Chicken Wings',
            description='Hot glazed wings with blue cheese',
            price=Decimal('10.00'),
            category_id=starters.id,
            is_available=True
        )
        dish3 = FoodItem(
            name='Artisan Burger',
            description='Gourmet wagyu patty on toasted brioche',
            price=Decimal('15.50'),
            category_id=mains.id,
            is_available=True
        )
        dish4 = FoodItem(
            name='Seasonal Catch',
            description='Fresh fish of the day',
            price=Decimal('22.00'),
            category_id=mains.id,
            is_available=False  # Out of stock
        )
        db.session.add_all([dish1, dish2, dish3, dish4])
        db.session.commit()
        return starters.id, mains.id, dish1.id, dish4.id


def test_customer_registration_success(client, app):
    """Test successful customer registration and role enforcement."""
    response = client.post('/auth/register', data={
        'name': 'Sarah Connor',
        'email': 'sarah@example.com',
        'password': 'SecurePassword123!',
        'confirm_password': 'SecurePassword123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Your account has been created successfully' in response.data

    with app.app_context():
        user = User.query.filter_by(email='sarah@example.com').first()
        assert user is not None
        assert user.name == 'Sarah Connor'
        assert user.role == 'customer'  # Never admin
        assert user.is_customer is True
        assert user.is_admin is False
        assert user.check_password('SecurePassword123!') is True


def test_customer_registration_duplicate_email(client, app):
    """Test that duplicate email registration is rejected with server-side validation error."""
    with app.app_context():
        existing = User(name='Existing User', email='dup@example.com', role='customer')
        existing.set_password('Password123!')
        db.session.add(existing)
        db.session.commit()

    response = client.post('/auth/register', data={
        'name': 'Duplicate Person',
        'email': 'dup@example.com',
        'password': 'AnotherPassword123!',
        'confirm_password': 'AnotherPassword123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'This email address is already registered' in response.data


def test_customer_registration_validation_errors(client):
    """Test short password and password mismatch errors."""
    # Password mismatch
    response = client.post('/auth/register', data={
        'name': 'Mismatch User',
        'email': 'mismatch@example.com',
        'password': 'Password123!',
        'confirm_password': 'DifferentPassword123!'
    })
    assert b'Passwords must match' in response.data

    # Short password
    response = client.post('/auth/register', data={
        'name': 'Short User',
        'email': 'short@example.com',
        'password': 'short',
        'confirm_password': 'short'
    })
    assert b'Password must be at least 8 characters long' in response.data


def test_login_invalid_credentials(client, app):
    """Test login failure with invalid email or incorrect password."""
    # Non-existent user
    response = client.post('/auth/login', data={
        'email': 'nonexistent@example.com',
        'password': 'Password123!'
    }, follow_redirects=True)
    assert b'Invalid email or password' in response.data

    # Wrong password for existing user
    with app.app_context():
        user = User(name='Bob', email='bob@example.com', role='customer')
        user.set_password('CorrectPassword123!')
        db.session.add(user)
        db.session.commit()

    response = client.post('/auth/login', data={
        'email': 'bob@example.com',
        'password': 'WrongPassword123!'
    }, follow_redirects=True)
    assert b'Invalid email or password' in response.data


def test_login_valid_customer_and_logout(client, app):
    """Test valid customer login session creation and subsequent logout."""
    with app.app_context():
        user = User(name='Gourmet Fan', email='fan@example.com', role='customer')
        user.set_password('DeliciousPass123!')
        db.session.add(user)
        db.session.commit()

    # Login
    login_res = client.post('/auth/login', data={
        'email': 'fan@example.com',
        'password': 'DeliciousPass123!'
    }, follow_redirects=True)
    assert login_res.status_code == 200
    assert b'Welcome back, Gourmet Fan!' in login_res.data
    assert b'Hello, Gourmet Fan' in login_res.data or b'Gourmet Fan' in login_res.data

    # Logout
    logout_res = client.post('/auth/logout', follow_redirects=True)
    assert logout_res.status_code == 200
    assert b'You have been logged out successfully' in logout_res.data
    assert b'Sign In' in logout_res.data


def test_login_admin_redirect(client, app):
    """Test that logging in as an administrator directs to admin dashboard."""
    with app.app_context():
        admin = User(name='Head Manager', email='admin@cravecart.com', role='admin')
        admin.set_password('AdminMaster123!')
        db.session.add(admin)
        db.session.commit()

    response = client.post('/auth/login', data={
        'email': 'admin@cravecart.com',
        'password': 'AdminMaster123!'
    }, follow_redirects=False)

    # Admin should be redirected to admin dashboard
    assert response.status_code == 302
    assert '/admin' in response.headers['Location']


def test_unauthorized_access_restrictions(client, app):
    """Test access control: anonymous redirects to login; customer gets 403 Forbidden."""
    # 1. Anonymous access to protected admin route -> redirects to login
    anon_res = client.get('/admin/dashboard')
    assert anon_res.status_code == 302
    assert '/auth/login' in anon_res.headers['Location']

    # 2. Customer login
    with app.app_context():
        cust = User(name='Plain Customer', email='cust@example.com', role='customer')
        cust.set_password('CustomerPass123!')
        db.session.add(cust)
        db.session.commit()

    client.post('/auth/login', data={
        'email': 'cust@example.com',
        'password': 'CustomerPass123!'
    })

    # Customer tries to access admin dashboard -> 403 Forbidden
    cust_res = client.get('/admin/dashboard')
    assert cust_res.status_code == 403
    assert b'403' in cust_res.data
    assert b'Access Denied' in cust_res.data


def test_menu_loading_and_filtering(client, app):
    """Test menu loading, category filtering, and keyword search."""
    starters_id, mains_id, _, _ = seed_test_dishes(app)

    # 1. Load entire menu
    response = client.get('/menu')
    assert response.status_code == 200
    assert b'Truffle Fries' in response.data
    assert b'Spicy Chicken Wings' in response.data
    assert b'Artisan Burger' in response.data

    # 2. Filter by Category: Starters
    starters_res = client.get(f'/menu?category={starters_id}')
    assert starters_res.status_code == 200
    assert b'Truffle Fries' in starters_res.data
    assert b'Spicy Chicken Wings' in starters_res.data
    assert b'Artisan Burger' not in starters_res.data

    # 3. Filter by Category: Mains
    mains_res = client.get(f'/menu?category={mains_id}')
    assert mains_res.status_code == 200
    assert b'Artisan Burger' in mains_res.data
    assert b'Truffle Fries' not in mains_res.data

    # 4. Search by keyword
    search_res = client.get('/menu?q=Truffle')
    assert search_res.status_code == 200
    assert b'Truffle Fries' in search_res.data
    assert b'Spicy Chicken Wings' not in search_res.data

    # 5. Search non-existent
    empty_res = client.get('/menu?q=NonExistentPizza123')
    assert empty_res.status_code == 200
    assert b'No matching dishes found' in empty_res.data


def test_food_detail_page(client, app):
    """Test individual food item detail page."""
    _, _, dish_id, sold_out_id = seed_test_dishes(app)

    # In-stock item
    response = client.get(f'/food/{dish_id}')
    assert response.status_code == 200
    assert b'Truffle Fries' in response.data
    assert b'Crispy russet fries with truffle oil' in response.data
    assert b'Add to Cart' in response.data
    assert b'In Stock & Ready' in response.data

    # Out of stock item
    sold_out_res = client.get(f'/food/{sold_out_id}')
    assert sold_out_res.status_code == 200
    assert b'Seasonal Catch' in sold_out_res.data
    assert b'Currently Sold Out' in sold_out_res.data

    # Non-existent item -> 404
    not_found_res = client.get('/food/99999')
    assert not_found_res.status_code == 404


def test_add_to_cart_and_cart_count(client, app):
    """Test adding items to session cart and verifying cart count in navigation."""
    _, _, dish_id, sold_out_id = seed_test_dishes(app)

    # Initially cart is empty
    home_res = client.get('/')
    assert b'id="cartBadgeCount">0</span>' in home_res.data

    # Add 2 of dish_id to cart
    add_res = client.post(f'/cart/add/{dish_id}', data={'quantity': '2'}, follow_redirects=True)
    assert add_res.status_code == 200
    assert b'Added 2x' in add_res.data
    assert b'Truffle Fries' in add_res.data
    assert b'id="cartBadgeCount">2</span>' in add_res.data

    # Add 1 more of dish_id
    client.post(f'/cart/add/{dish_id}', data={'quantity': '1'}, follow_redirects=True)
    cart_page_res = client.get('/cart')
    assert cart_page_res.status_code == 200
    assert b'Truffle Fries' in cart_page_res.data
    assert b'id="cartBadgeCount">3</span>' in cart_page_res.data

    # Adding an out-of-stock item is rejected
    sold_out_res = client.post(f'/cart/add/{sold_out_id}', data={'quantity': '1'}, follow_redirects=True)
    assert b'is currently sold out' in sold_out_res.data
