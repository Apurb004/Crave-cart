from decimal import Decimal
import click
from flask import Flask
from app.extensions import db
from app.models import User, Category, FoodItem


def register_commands(app: Flask) -> None:
    """Register custom Flask CLI commands."""

    @app.cli.command('init-db')
    @click.option('--drop', is_flag=True, help='Drop existing tables before creating new ones.')
    def init_db(drop):
        """Initialize database tables."""
        if drop:
            if click.confirm('Are you sure you want to drop all existing tables?', abort=True):
                db.drop_all()
                click.echo('Dropped all existing database tables.')
        db.create_all()
        click.echo('✓ Database tables initialized successfully.')

    @app.cli.command('create-admin')
    def create_admin():
        """Create a new administrator account securely through interactive prompt."""
        click.echo('\n--- CraveCart: Create Administrator Account ---')
        name = click.prompt('Administrator Name', default='Restaurant Manager')
        email = click.prompt('Administrator Email').strip().lower()

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            if existing_user.is_admin:
                click.echo(f"Notice: User with email '{email}' already exists and is already an Administrator.")
                return
            if click.confirm(f"User with email '{email}' already exists as '{existing_user.role}'. Promote to admin?"):
                existing_user.role = 'admin'
                db.session.commit()
                click.echo(f"✓ User '{email}' promoted to Administrator.")
            return

        # Secure password input (no hardcoded credentials)
        password = click.prompt(
            'Administrator Password',
            hide_input=True,
            confirmation_prompt=True
        )

        if len(password) < 8:
            click.echo('Error: Password must be at least 8 characters long.')
            return

        admin = User(
            name=name,
            email=email,
            role='admin'
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()

        click.echo(f"✓ Administrator account '{email}' created successfully.")

    @app.cli.command('seed-db')
    def seed_db():
        """Seed demonstration categories and food items."""
        click.echo('Seeding demonstration food categories and items...')

        # Demo Categories
        demo_categories = [
            {
                'name': 'Starters & Appetizers',
                'description': 'Crispy, savory finger foods and gourmet bites to kick off your meal.'
            },
            {
                'name': 'Main Course',
                'description': 'Hearty, slow-cooked specialties, artisanal pastas, and wholesome bowls.'
            },
            {
                'name': 'Artisan Pizzas & Burgers',
                'description': 'Woodfired sourdough crusts and handcrafted flame-grilled gourmet burgers.'
            },
            {
                'name': 'Desserts & Sweets',
                'description': 'Decadent chocolate cakes, layered pastries, and artisanal ice creams.'
            },
            {
                'name': 'Beverages & Mocktails',
                'description': 'Chilled botanical mocktails, fresh pressed fruit juices, and cold brews.'
            }
        ]

        categories_map = {}
        for cat_data in demo_categories:
            category = Category.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = Category(name=cat_data['name'], description=cat_data['description'])
                db.session.add(category)
                db.session.flush()
                click.echo(f"  + Added category: {category.name}")
            categories_map[cat_data['name']] = category

        # Demo Food Items
        demo_items = [
            # Starters
            {
                'name': 'Crispy Truffle Fries',
                'description': 'Hand-cut russet potatoes tossed with white truffle oil, grated parmesan, and rosemary garlic aioli.',
                'price': Decimal('7.50'),
                'image_url': 'https://images.unsplash.com/photo-1576107232684-1279f3908594?w=600&q=80',
                'category_name': 'Starters & Appetizers',
                'is_available': True
            },
            {
                'name': 'Stuffed Herb Portobello',
                'description': 'Oven-roasted mushrooms filled with herbed ricotta, toasted pine nuts, and balsamic reduction.',
                'price': Decimal('9.99'),
                'image_url': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&q=80',
                'category_name': 'Starters & Appetizers',
                'is_available': True
            },
            {
                'name': 'Fiery Buffalo Cauliflower Wings',
                'description': 'Crisp panko-crusted florets tossed in tangy buffalo glaze with house ranch dip.',
                'price': Decimal('8.25'),
                'image_url': 'https://images.unsplash.com/photo-1562967914-608f82629710?w=600&q=80',
                'category_name': 'Starters & Appetizers',
                'is_available': True
            },

            # Main Course
            {
                'name': 'Slow-Cooked Herb Chicken Roulade',
                'description': 'Pan-seared tender chicken breast rolled with spinach and sun-dried tomatoes, served with roasted baby potatoes.',
                'price': Decimal('16.75'),
                'image_url': 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=600&q=80',
                'category_name': 'Main Course',
                'is_available': True
            },
            {
                'name': 'Wild Mushroom Risotto',
                'description': 'Creamy arborio rice with porcini and cremini mushrooms, finished with aged pecorino and thyme.',
                'price': Decimal('14.50'),
                'image_url': 'https://images.unsplash.com/photo-1633964913295-ceb43826e7c9?w=600&q=80',
                'category_name': 'Main Course',
                'is_available': True
            },
            {
                'name': 'Grilled Salmon with Lemon Butter',
                'description': 'Atlantic salmon fillet grilled to perfection, served with asparagus spears and velvety lemon dill sauce.',
                'price': Decimal('19.50'),
                'image_url': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=600&q=80',
                'category_name': 'Main Course',
                'is_available': True
            },

            # Pizzas & Burgers
            {
                'name': 'Smoked Mozzarella & Basil Pizza',
                'description': 'Slow-fermented sourdough base, San Marzano tomato sauce, smoked mozzarella, and fresh sweet basil.',
                'price': Decimal('13.25'),
                'image_url': 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&q=80',
                'category_name': 'Artisan Pizzas & Burgers',
                'is_available': True
            },
            {
                'name': 'Crave Gourmet Wagyu Burger',
                'description': 'Prime ground beef patty, caramelised shallots, aged cheddar, arugula, and smoked chipotle mayo on brioche.',
                'price': Decimal('15.00'),
                'image_url': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&q=80',
                'category_name': 'Artisan Pizzas & Burgers',
                'is_available': True
            },

            # Desserts
            {
                'name': 'Belgian Dark Chocolate Lava Cake',
                'description': 'Warm molten chocolate center cake served with Madagascar bourbon vanilla bean gelato.',
                'price': Decimal('8.50'),
                'image_url': 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=600&q=80',
                'category_name': 'Desserts & Sweets',
                'is_available': True
            },
            {
                'name': 'Classic Venetian Tiramisu',
                'description': 'Espresso-soaked savoiardi ladyfingers layered with whipped mascarpone cream and dusted with raw cacao.',
                'price': Decimal('7.75'),
                'image_url': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=600&q=80',
                'category_name': 'Desserts & Sweets',
                'is_available': True
            },

            # Beverages
            {
                'name': 'Sparkling Citrus Berry Cooler',
                'description': 'Infused wild raspberries, crushed mint leaves, freshly squeezed lime, and fizzy mineral soda.',
                'price': Decimal('5.25'),
                'image_url': 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&q=80',
                'category_name': 'Beverages & Mocktails',
                'is_available': True
            },
            {
                'name': 'Iced Vanilla Cold Brew',
                'description': 'Slow-steeped Arabica coffee over ice, touched with homemade vanilla syrup and a splash of oat milk.',
                'price': Decimal('5.75'),
                'image_url': 'https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?w=600&q=80',
                'category_name': 'Beverages & Mocktails',
                'is_available': True
            }
        ]

        items_added = 0
        for item_data in demo_items:
            category = categories_map.get(item_data['category_name'])
            existing_item = FoodItem.query.filter_by(name=item_data['name']).first()
            if not existing_item and category:
                food = FoodItem(
                    name=item_data['name'],
                    description=item_data['description'],
                    price=item_data['price'],
                    image_url=item_data['image_url'],
                    category_id=category.id,
                    is_available=item_data['is_available']
                )
                db.session.add(food)
                items_added += 1
                click.echo(f"  + Added food item: {food.name} (${food.price})")

        db.session.commit()
        click.echo(f"✓ Database seeding complete! Added {items_added} new items.")
