from flask_jwt_extended import create_access_token, create_refresh_token
from app.models import User
from app import db
from app.config import Config
from datetime import datetime

class AuthService:
    @staticmethod
    def authenticate_admin(email, password):
        """Authenticate admin user"""
        if email == Config.ADMIN_EMAIL and password == Config.ADMIN_PASSWORD:
            admin = User.query.filter_by(email=email).first()
            if not admin:
                admin = User(
                    email=email,
                    full_name='Quiz Master Admin',
                    is_admin=True
                )
                admin.set_password(Config.ADMIN_PASSWORD)
                db.session.add(admin)
                db.session.commit()
            return admin
        return None

    @staticmethod
    def authenticate_user(email, password):
        """Authenticate regular user"""
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def create_tokens(user):
        """Create access and refresh tokens for user"""
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_admin': user.is_admin
            }
        }

    @staticmethod
    def register_user(email, password, full_name, qualification=None, date_of_birth=None):
        """Register a new user"""
        if User.query.filter_by(email=email).first():
            return None, 'Email already registered'
        
        # Convert date string to date object if provided
        if date_of_birth and isinstance(date_of_birth, str):
            try:
                date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                return None, 'Invalid date format. Use YYYY-MM-DD'
        
        user = User(
            email=email,
            full_name=full_name,
            qualification=qualification,
            date_of_birth=date_of_birth,
            is_admin=False
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user, None 