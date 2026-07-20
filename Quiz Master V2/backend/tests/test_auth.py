import pytest
from app import create_app, db
from app.models import User
from app.config import Config

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_admin_login(client):
    response = client.post('/api/auth/admin/login', json={
        'email': Config.ADMIN_EMAIL,
        'password': Config.ADMIN_PASSWORD
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['is_admin'] == True

def test_user_registration(client):
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'full_name': 'Test User',
        'qualification': 'B.Tech',
        'date_of_birth': '2000-01-01'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['is_admin'] == False

def test_user_login(client):
    # First register a user
    client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'full_name': 'Test User'
    })
    
    # Then try to login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data

def test_invalid_login(client):
    response = client.post('/api/auth/login', json={
        'email': 'wrong@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

@pytest.mark.skip(reason="Protected route functionality to be implemented later")
def test_protected_route(client):
    # Login as admin
    response = client.post('/api/auth/admin/login', json={
        'email': Config.ADMIN_EMAIL,
        'password': Config.ADMIN_PASSWORD
    })
    token = response.get_json()['access_token']
    
    # Try to access protected route
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = client.get('/api/admin/dashboard', headers=headers)
    assert response.status_code == 200 