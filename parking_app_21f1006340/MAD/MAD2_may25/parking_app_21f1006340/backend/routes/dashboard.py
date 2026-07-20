from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/admin/dashboard')
@jwt_required()
def admin_dashboard():
    identity = get_jwt_identity()
    if identity.get('role') != 'admin':
        return jsonify({"msg": "Access denied, admins only"}), 403
    return jsonify({"msg": "Welcome to Admin Dashboard"})

@dashboard_bp.route('/user/dashboard')
@jwt_required()
def user_dashboard():
    identity = get_jwt_identity()
    if identity.get('role') != 'user':
        return jsonify({"msg": "Access denied, users only"}), 403
    return jsonify({"msg": f"Welcome to User Dashboard, {identity.get('email')}!"})
