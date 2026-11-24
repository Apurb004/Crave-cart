from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import auth_bp
from app.extensions import db
from app.models import User
from app.forms import RegistrationForm, LoginForm
from app.utils import is_safe_url


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration endpoint. Prevents admin privilege escalation."""
    if current_user.is_authenticated:
        return redirect(url_for('customer.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.strip().lower(),
            role='customer'  # Strictly customer role
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created successfully! Please sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Customer & Administrator login endpoint with safe redirection."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('customer.index'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.name}!', 'success')

            # Handle post-login redirection securely
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)

            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('customer.index'))
        else:
            flash('Invalid email or password. Please verify your credentials and try again.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Terminates active user session."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('customer.index'))
