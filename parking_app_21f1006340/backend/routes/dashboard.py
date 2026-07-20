from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/admin/dashboard')
@jwt_required()
def admin_dashboard():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"msg": "Access denied, admins only"}), 403

    user_id = get_jwt_identity()
    return jsonify({
        "msg": "Welcome to Admin Dashboard",
        "admin_id": int(user_id) if user_id is not None else None,
        "email": claims.get("email")
    })


@dashboard_bp.route('/user/dashboard')
@jwt_required()
def user_dashboard():
    claims = get_jwt()
    if claims.get("is_admin"):
        return jsonify({"msg": "Access denied, users only"}), 403

    user_id = get_jwt_identity()
    return jsonify({
        "msg": "Welcome to User Dashboard",
        "user_id": int(user_id) if user_id is not None else None,
        "email": claims.get("email")
    })
