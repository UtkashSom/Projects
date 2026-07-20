from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import logging
import sys

# Import routes after app is created to avoid circular imports
from routes import all_routes
from models import Base, engine

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# In app.py, update the CORS configuration to:
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
        "supports_credentials": True
    }
})

jwt = JWTManager(app)

# Register blueprint only if not already registered
blueprint_name = all_routes.name
if blueprint_name not in app.blueprints:
    app.register_blueprint(all_routes, url_prefix='/api')
else:
    print(f"Warning: Blueprint '{blueprint_name}' is already registered.", file=sys.stderr)

@app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.path}")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Body: {request.get_data()}")

@app.after_request
def after_request(response):
    # Add CORS headers
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8080')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    
    # Log the response
    logger.info(f"Response: {response.status}")
    return response

@app.route('/')
def index():
    return jsonify({"msg": "Vehicle Parking App Backend Running"})

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    app.run(debug=True)