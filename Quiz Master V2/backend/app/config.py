import os
from datetime import timedelta

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///quiz_master.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Admin credentials (in production, use environment variables)
    ADMIN_EMAIL = 'admin@quizmaster.com'
    ADMIN_PASSWORD = 'admin123' 