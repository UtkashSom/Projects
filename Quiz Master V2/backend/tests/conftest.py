import os
import sys
import pytest
from datetime import timedelta
from flask_jwt_extended import JWTManager

# Add the backend directory to the Python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

from app import create_app, db
from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=10)

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client() 