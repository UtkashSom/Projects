from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_mail import Mail
from celery import Celery
import os
from dotenv import load_dotenv
from app.config import Config

# Load environment variables
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()
mail = Mail()
celery = Celery()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    celery.conf.update(app.config)
    
    # Register blueprints
    from app.routes import auth, admin, user, quiz
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    app.register_blueprint(user.bp, url_prefix='/api/user')
    app.register_blueprint(quiz.bp, url_prefix='/api/quiz')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
    return app 