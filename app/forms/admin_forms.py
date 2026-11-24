from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, InputRequired


class CategoryForm(FlaskForm):
    """Form for adding and editing food categories."""
    name = StringField(
        'Category Name',
        validators=[
            DataRequired(message='Category name is required.'),
            Length(min=2, max=80, message='Category name must be between 2 and 80 characters.')
        ],
        render_kw={'placeholder': 'e.g. Artisanal Starters', 'autocomplete': 'off'}
    )
    description = TextAreaField(
        'Description (Optional)',
        validators=[
            Optional(),
            Length(max=255, message='Description cannot exceed 255 characters.')
        ],
        render_kw={'placeholder': 'Brief description of dishes in this section...', 'rows': 2}
    )
    submit = SubmitField('Save Category')


class FoodItemForm(FlaskForm):
    """Form for creating and editing dishes in the menu catalog."""
    name = StringField(
        'Dish Name',
        validators=[
            DataRequired(message='Dish name is required.'),
            Length(min=2, max=120, message='Dish name must be between 2 and 120 characters.')
        ],
        render_kw={'placeholder': 'e.g. Truffle Mushroom Tagliatelle', 'autocomplete': 'off'}
    )
    category_id = SelectField(
        'Category',
        coerce=int,
        validators=[DataRequired(message='Please assign a category.')]
    )
    price = DecimalField(
        'Price ($ USD)',
        places=2,
        validators=[
            InputRequired(message='Please set a unit price.'),
            NumberRange(min=0.01, max=999.99, message='Price must be between $0.01 and $999.99.')
        ],
        render_kw={'placeholder': 'e.g. 14.50', 'step': '0.01'}
    )
    description = TextAreaField(
        'Culinary Description',
        validators=[
            Optional(),
            Length(max=500, message='Description cannot exceed 500 characters.')
        ],
        render_kw={'placeholder': 'Describe ingredients, preparation style, allergen notes...', 'rows': 3}
    )
    image_url = StringField(
        'Food Image URL',
        validators=[
            Optional(),
            Length(max=255, message='URL cannot exceed 255 characters.')
        ],
        render_kw={'placeholder': 'https://images.unsplash.com/... or /static/images/...'}
    )
    is_available = BooleanField('In Stock & Available for Ordering', default=True)
    submit = SubmitField('Save Dish')


class OrderStatusForm(FlaskForm):
    """Form for administrative order fulfillment status transitions."""
    status = SelectField(
        'Target Status',
        validators=[DataRequired(message='Please choose a valid status.')]
    )
    submit = SubmitField('Update Order Status')
