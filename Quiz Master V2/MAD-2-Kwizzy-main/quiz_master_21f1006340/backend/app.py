from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress
from flask_caching import Cache
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///quiz_master.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour

# Initialize extensions
CORS(app)
api = Api(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
Compress(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
socketio = SocketIO(app, cors_allowed_origins="*")

# Import routes after app is created
from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
