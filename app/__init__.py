import os
from flask import Flask, render_template, session
from config import config_by_name
from app.extensions import db, login_manager, csrf
from app.commands import register_commands


def create_app(config_name: str = None) -> Flask:
    """
    Application factory for CraveCart.
    Initializes extensions, registers blueprints, CLI commands, and error handlers.
    """
    app = Flask(__name__)

    # Determine configuration environment
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development').lower()
        if config_name not in config_by_name:
            config_name = 'default'

    app.config.from_object(config_by_name[config_name])

    # Initialize extensions with app context
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.auth import auth_bp
    from app.customer import customer_bp
    from app.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(admin_bp)

    # Register custom CLI commands
    register_commands(app)

    # Register HTTP error handlers
    register_error_handlers(app)

    # Register global context processors
    @app.context_processor
    def inject_global_data():
        cart = session.get('cart', {})
        cart_count = sum(cart.values()) if isinstance(cart, dict) else 0
        return {
            'app_name': 'CraveCart',
            'restaurant_tagline': 'Gourmet Flavors Delivered to Your Door',
            'cart_count': cart_count
        }

    return app


def register_error_handlers(app: Flask) -> None:
    """Register custom templates for standard HTTP errors."""

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
