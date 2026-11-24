import os
from app import create_app
from app.extensions import db
from app.models import User, Category, FoodItem, Order, OrderItem

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """Make database models accessible in `flask shell`."""
    return {
        'db': db,
        'User': User,
        'Category': Category,
        'FoodItem': FoodItem,
        'Order': Order,
        'OrderItem': OrderItem
    }


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
