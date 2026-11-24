from decimal import Decimal
import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import User, Category, FoodItem, Order, OrderItem


def test_user_password_hashing(app):
    """Test user password hashing and verification."""
    user = User(name='Alice Chef', email='alice@example.com', role='customer')
    user.set_password('SecretPass123')

    assert user.password_hash != 'SecretPass123'
    assert user.check_password('SecretPass123') is True
    assert user.check_password('WrongPass') is False
    assert user.is_customer is True
    assert user.is_admin is False


def test_user_roles(app):
    """Test user role checking properties."""
    admin = User(name='Manager Bob', email='admin@example.com', role='admin')
    admin.set_password('AdminPass123')
    db.session.add(admin)
    db.session.commit()

    assert admin.is_admin is True
    assert admin.is_customer is False


def test_user_unique_email(app):
    """Test that email uniqueness is enforced in database."""
    user1 = User(name='User One', email='duplicate@example.com', role='customer')
    user1.set_password('Pass1234')
    db.session.add(user1)
    db.session.commit()

    user2 = User(name='User Two', email='duplicate@example.com', role='customer')
    user2.set_password('Pass5678')
    db.session.add(user2)

    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_category_and_food_item_relationship(app):
    """Test Category to FoodItem relationship and foreign keys."""
    category = Category(name='Starters', description='Appetizers and snacks')
    db.session.add(category)
    db.session.commit()

    item1 = FoodItem(
        name='Garlic Bread',
        description='Toasted baguette with herb butter',
        price=Decimal('5.50'),
        image_url='/static/images/garlic-bread.jpg',
        category_id=category.id,
        is_available=True
    )
    item2 = FoodItem(
        name='Tomato Bruschetta',
        description='Fresh basil and tomatoes on crusty bread',
        price=Decimal('7.25'),
        image_url='/static/images/bruschetta.jpg',
        category_id=category.id,
        is_available=True
    )
    db.session.add_all([item1, item2])
    db.session.commit()

    # Verify relationship
    assert len(category.food_items) == 2
    assert category.food_items[0].name in ['Garlic Bread', 'Tomato Bruschetta']
    assert item1.category.name == 'Starters'
    assert isinstance(item1.price, Decimal)
    assert item1.price == Decimal('5.50')


def test_order_and_order_item_lifecycle(app):
    """
    Test complete order creation, line item calculations,
    and preservation of historical price snapshots.
    """
    # Create customer
    customer = User(name='John Doe', email='john@example.com', role='customer')
    customer.set_password('Customer123')
    db.session.add(customer)

    # Create category & food item
    category = Category(name='Mains', description='Main courses')
    db.session.add(category)
    db.session.flush()

    dish = FoodItem(
        name='Truffle Pasta',
        description='Handmade tagliatelle with fresh black truffle',
        price=Decimal('18.50'),
        category_id=category.id,
        is_available=True
    )
    db.session.add(dish)
    db.session.commit()

    # Create order
    order = Order(
        user_id=customer.id,
        total_amount=Decimal('0.00'),
        delivery_address='123 Gourmet Lane, Food City',
        phone_number='555-0199',
        payment_method='Cash on Delivery',
        status=Order.STATUS_PENDING
    )
    db.session.add(order)
    db.session.flush()

    order.order_number = order.generate_order_number()

    # Create order item
    order_item = OrderItem(
        order_id=order.id,
        food_item_id=dish.id,
        item_name=dish.name,
        unit_price=dish.price,
        quantity=2,
        subtotal=Decimal('0.00')
    )
    order_item.calculate_subtotal()
    db.session.add(order_item)

    # Recalculate order total
    order.recalculate_total()
    db.session.commit()

    # Assertions
    assert order.order_number.startswith('CRV-')
    assert order_item.subtotal == Decimal('37.00')
    assert order.total_amount == Decimal('37.00')
    assert len(order.items) == 1
    assert order.items[0].item_name == 'Truffle Pasta'

    # Test historical snapshot integrity:
    # If menu item price changes later, the past order item MUST retain original price!
    dish.price = Decimal('25.00')
    dish.name = 'Truffle Pasta (Updated Recipe)'
    db.session.commit()

    reloaded_order = db.session.get(Order, order.id)
    assert reloaded_order.items[0].unit_price == Decimal('18.50')
    assert reloaded_order.items[0].item_name == 'Truffle Pasta'
    assert reloaded_order.total_amount == Decimal('37.00')


def test_order_cascade_delete(app):
    """Test that deleting an order cascades to its order items."""
    user = User(name='Sam', email='sam@example.com', role='customer')
    user.set_password('Pass1234')
    db.session.add(user)
    db.session.flush()

    order = Order(
        user_id=user.id,
        total_amount=Decimal('15.00'),
        delivery_address='456 Elm St',
        phone_number='555-4567',
        payment_method='Cash on Delivery'
    )
    db.session.add(order)
    db.session.flush()

    item = OrderItem(
        order_id=order.id,
        food_item_id=None,
        item_name='Sample Dish',
        unit_price=Decimal('15.00'),
        quantity=1,
        subtotal=Decimal('15.00')
    )
    db.session.add(item)
    db.session.commit()

    item_id = item.id
    db.session.delete(order)
    db.session.commit()

    # Verify OrderItem is deleted along with Order
    assert db.session.get(OrderItem, item_id) is None
