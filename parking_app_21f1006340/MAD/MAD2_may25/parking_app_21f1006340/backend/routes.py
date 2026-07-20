from flask import Blueprint
from .auth import auth_bp
from .dashboard import dashboard_bp
from .admin_lot import admin_lot_bp

all_routes = Blueprint('all_routes', __name__)

all_routes.register_blueprint(auth_bp, url_prefix='/auth')
all_routes.register_blueprint(dashboard_bp, url_prefix='/dashboard')
all_routes.register_blueprint(admin_lot_bp, url_prefix='/admin')
