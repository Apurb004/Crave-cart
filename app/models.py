from datetime import datetime
from decimal import Decimal
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    """
    User entity representing Customers and Administrators.
    Uses Flask-Login UserMixin for session management.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer', index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    orders = db.relationship(
        'Order',
        back_populates='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def set_password(self, password: str) -> None:
        """Hash and store the user's password."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password: str) -> bool:
        """Verify the candidate password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        """Check if the user has administrative privileges."""
        return self.role == 'admin'

    @property
    def is_customer(self) -> bool:
        """Check if the user is a standard customer."""
        return self.role == 'customer'

    def __repr__(self) -> str:
        return f"<User id={self.id} email='{self.email}' role='{self.role}'>"


@login_manager.user_loader
def load_user(user_id: str):
    """Flask-Login user loader callback."""
    return db.session.get(User, int(user_id))


class Category(db.Model):
    """
    Food category entity for classifying menu items
    (e.g., Starters, Main Course, Desserts, Beverages).
    """
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    food_items = db.relationship(
        'FoodItem',
        back_populates='category',
        cascade='all, delete-orphan',
        lazy='select'
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name='{self.name}'>"


class FoodItem(db.Model):
    """
    Food item entity in the restaurant catalog with pricing,
    availability status, and category association.
    """
    __tablename__ = 'food_items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2, asdecimal=True), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    is_available = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    category = db.relationship('Category', back_populates='food_items')
    order_items = db.relationship('OrderItem', back_populates='food_item')

    def __repr__(self) -> str:
        return f"<FoodItem id={self.id} name='{self.name}' price={self.price} available={self.is_available}>"


class Order(db.Model):
    """
    Order entity recording customer purchases, delivery coordinates,
    payment method (COD), and fulfillment status.
    """
    __tablename__ = 'orders'

    # Order lifecycle statuses
    STATUS_PLACED = 'PLACED'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_PREPARING = 'PREPARING'
    STATUS_OUT_FOR_DELIVERY = 'OUT FOR DELIVERY'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_CANCELLED = 'CANCELLED'

    # Backward-compatibility alias
    STATUS_PENDING = STATUS_PLACED

    ALL_STATUSES = [
        STATUS_PLACED,
        STATUS_CONFIRMED,
        STATUS_PREPARING,
        STATUS_OUT_FOR_DELIVERY,
        STATUS_DELIVERED,
        STATUS_CANCELLED,
    ]

    # Valid administrator status transition workflow
    VALID_TRANSITIONS = {
        STATUS_PLACED: [STATUS_CONFIRMED, STATUS_CANCELLED],
        STATUS_CONFIRMED: [STATUS_PREPARING, STATUS_CANCELLED],
        STATUS_PREPARING: [STATUS_OUT_FOR_DELIVERY],
        STATUS_OUT_FOR_DELIVERY: [STATUS_DELIVERED],
        STATUS_DELIVERED: [],
        STATUS_CANCELLED: []
    }

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(32), unique=True, nullable=True, index=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    customer_name = db.Column(db.String(100), nullable=True)
    total_amount = db.Column(db.Numeric(10, 2, asdecimal=True), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False, default='Cash on Delivery')
    status = db.Column(db.String(30), nullable=False, default=STATUS_PLACED, index=True)
    order_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    user = db.relationship('User', back_populates='orders')
    items = db.relationship(
        'OrderItem',
        back_populates='order',
        cascade='all, delete-orphan',
        lazy='select'
    )

    @property
    def can_cancel(self) -> bool:
        """Customers may cancel an order only while its status is PLACED."""
        return self.status in (self.STATUS_PLACED, 'Pending', 'Placed')

    def can_transition_to(self, new_status: str) -> bool:
        """Check if transition from current status to new_status is valid."""
        current = self.status.upper() if self.status else self.STATUS_PLACED
        return new_status in self.VALID_TRANSITIONS.get(current, [])

    def allowed_transitions(self) -> list:
        """List of valid next statuses from current status."""
        current = self.status.upper() if self.status else self.STATUS_PLACED
        return self.VALID_TRANSITIONS.get(current, [])

    @property
    def display_customer_name(self) -> str:
        """Fallback to user account name if customer_name was not captured."""
        return self.customer_name or (self.user.name if self.user else 'Valued Customer')

    def generate_order_number(self) -> str:
        """Generate human-readable order number (e.g., CRV-YYYYMMDD-ID)."""
        date_str = self.created_at.strftime('%Y%m%d') if self.created_at else datetime.utcnow().strftime('%Y%m%d')
        return f"CRV-{date_str}-{self.id:04d}"

    def recalculate_total(self) -> Decimal:
        """Recalculate order total from current order items."""
        total = sum((item.subtotal for item in self.items), Decimal('0.00'))
        self.total_amount = total.quantize(Decimal('0.01'))
        return self.total_amount

    def __repr__(self) -> str:
        return f"<Order id={self.id} num='{self.order_number}' status='{self.status}' total={self.total_amount}>"


class OrderItem(db.Model):
    """
    Itemized line item for an order.
    Preserves historical snapshot of food item name and unit price
    at the exact moment of order placement.
    """
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer,
        db.ForeignKey('orders.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    food_item_id = db.Column(
        db.Integer,
        db.ForeignKey('food_items.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    item_name = db.Column(db.String(120), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2, asdecimal=True), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    subtotal = db.Column(db.Numeric(10, 2, asdecimal=True), nullable=False)

    # Relationships
    order = db.relationship('Order', back_populates='items')
    food_item = db.relationship('FoodItem', back_populates='order_items')

    def calculate_subtotal(self) -> Decimal:
        """Calculate line subtotal from unit_price and quantity."""
        sub = (Decimal(str(self.unit_price)) * self.quantity).quantize(Decimal('0.01'))
        self.subtotal = sub
        return self.subtotal

    def __repr__(self) -> str:
        return f"<OrderItem id={self.id} item='{self.item_name}' qty={self.quantity} subtotal={self.subtotal}>"
