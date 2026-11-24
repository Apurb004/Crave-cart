from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    """Customer registration form with robust server-side validation."""
    name = StringField(
        'Full Name',
        validators=[
            DataRequired(message='Please provide your full name.'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters.')
        ],
        render_kw={'placeholder': 'e.g. Jane Doe', 'autocomplete': 'name'}
    )
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Please provide your email address.'),
            Email(message='Please enter a valid email address.'),
            Length(max=120, message='Email cannot exceed 120 characters.')
        ],
        render_kw={'placeholder': 'you@example.com', 'autocomplete': 'email'}
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Please enter a password.'),
            Length(min=8, max=64, message='Password must be at least 8 characters long.')
        ],
        render_kw={'placeholder': 'At least 8 characters', 'autocomplete': 'new-password'}
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password.'),
            EqualTo('password', message='Passwords must match.')
        ],
        render_kw={'placeholder': 'Re-enter your password', 'autocomplete': 'new-password'}
    )
    submit = SubmitField('Create Account')

    def validate_email(self, field):
        """Ensure email uniqueness across the platform."""
        sanitized_email = field.data.strip().lower()
        if User.query.filter_by(email=sanitized_email).first():
            raise ValidationError('This email address is already registered. Please sign in.')


class LoginForm(FlaskForm):
    """Customer & Administrator login form."""
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Please enter your email address.'),
            Email(message='Please enter a valid email address.')
        ],
        render_kw={'placeholder': 'you@example.com', 'autocomplete': 'email'}
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Please enter your password.')
        ],
        render_kw={'placeholder': 'Enter your password', 'autocomplete': 'current-password'}
    )
    remember_me = BooleanField('Remember me on this device')
    submit = SubmitField('Sign In')
