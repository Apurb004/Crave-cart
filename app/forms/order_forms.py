from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class CheckoutForm(FlaskForm):
    """Checkout form capturing customer delivery coordinates and contact info."""
    customer_name = StringField(
        'Recipient Full Name',
        validators=[
            DataRequired(message='Please provide the recipient name.'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters.')
        ],
        render_kw={'placeholder': 'e.g. Alex Morgan', 'autocomplete': 'name'}
    )
    phone_number = StringField(
        'Contact Phone Number',
        validators=[
            DataRequired(message='Please provide a contact phone number for delivery.'),
            Length(min=7, max=20, message='Please enter a valid phone number.')
        ],
        render_kw={'placeholder': 'e.g. +1 555-0199', 'autocomplete': 'tel'}
    )
    delivery_address = TextAreaField(
        'Delivery Street Address',
        validators=[
            DataRequired(message='Please provide your complete delivery street address.'),
            Length(min=8, max=500, message='Address must be at least 8 characters long.')
        ],
        render_kw={
            'placeholder': 'Apartment / House number, Street name, Landmark, City',
            'rows': 3,
            'autocomplete': 'street-address'
        }
    )
    order_notes = TextAreaField(
        'Delivery / Preparation Notes (Optional)',
        validators=[
            Optional(),
            Length(max=300, message='Instructions cannot exceed 300 characters.')
        ],
        render_kw={
            'placeholder': 'e.g. Ring the bell twice, leave at reception, extra napkins...',
            'rows': 2
        }
    )
    submit = SubmitField('Place Order – Cash on Delivery')
