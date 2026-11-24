from app.models import User, Category, FoodItem


def test_home_and_menu_routes(client):
    """Test that public endpoints render successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'CraveCart' in response.data

    response = client.get('/menu')
    assert response.status_code == 200
    assert b'Menu' in response.data


def test_auth_placeholder_routes(client):
    """Test that auth endpoints render successfully."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Welcome Back' in response.data

    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Join CraveCart' in response.data


def test_init_db_command(runner, app):
    """Test flask init-db CLI command."""
    result = runner.invoke(args=['init-db'])
    assert result.exit_code == 0
    assert 'Database tables initialized successfully' in result.output


def test_seed_db_command(runner, app):
    """Test flask seed-db CLI command."""
    result = runner.invoke(args=['seed-db'])
    assert result.exit_code == 0
    assert 'Database seeding complete' in result.output

    with app.app_context():
        assert Category.query.count() >= 5
        assert FoodItem.query.count() >= 10


def test_create_admin_command(runner, app):
    """Test interactive admin creation CLI command."""
    # Simulate input: Name, Email, Password, Password confirmation
    simulated_input = "Head Chef\nchef@cravecart.com\nSuperSecret123!\nSuperSecret123!\n"
    result = runner.invoke(args=['create-admin'], input=simulated_input)

    assert result.exit_code == 0
    assert "Administrator account 'chef@cravecart.com' created successfully" in result.output

    with app.app_context():
        admin = User.query.filter_by(email='chef@cravecart.com').first()
        assert admin is not None
        assert admin.name == 'Head Chef'
        assert admin.is_admin is True
        assert admin.check_password('SuperSecret123!') is True
