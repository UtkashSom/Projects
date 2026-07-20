# Configuration settings can be placed here
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = 'redis://localhost:6379/0'
