from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import redis

app = Flask(__name__)
CORS(app)  # Allow Cross-Origin Requests

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Redis setup
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Importing routes
from routes.routes import *

if __name__ == '__main__':
    db.create_all()  # Create tables
    app.run(debug=True)
