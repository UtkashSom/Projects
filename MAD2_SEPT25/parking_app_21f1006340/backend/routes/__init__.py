from flask import Blueprint
from .auth import auth_bp
from .admin_lot import admin_bp as admin_lot_bp
from .user_parking import user_parking_bp
from .export_jobs import export_bp

all_routes = Blueprint("all_routes", __name__)

all_routes.register_blueprint(auth_bp, url_prefix="/auth")
all_routes.register_blueprint(admin_lot_bp, url_prefix="/admin")
all_routes.register_blueprint(user_parking_bp, url_prefix="/user")
all_routes.register_blueprint(export_bp, url_prefix="/jobs")
