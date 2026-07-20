from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth import AuthService
from app.utils.decorators import admin_required, user_required
from app.models.user import User

bp = Blueprint('auth', __name__)

@bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'msg': 'Missing email or password'}), 400
    
    admin = AuthService.authenticate_admin(email, password)
    if not admin:
        return jsonify({'msg': 'Invalid admin credentials'}), 401
    
    tokens = AuthService.create_tokens(admin)
    return jsonify(tokens), 200

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    qualification = data.get('qualification')
    date_of_birth = data.get('date_of_birth')
    
    if not all([email, password, full_name]):
        return jsonify({'msg': 'Missing required fields'}), 400
    
    user, error = AuthService.register_user(
        email=email,
        password=password,
        full_name=full_name,
        qualification=qualification,
        date_of_birth=date_of_birth
    )
    
    if error:
        return jsonify({'msg': error}), 400
    
    tokens = AuthService.create_tokens(user)
    return jsonify(tokens), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'msg': 'Missing email or password'}), 400
    
    user = AuthService.authenticate_user(email, password)
    if not user:
        return jsonify({'msg': 'Invalid credentials'}), 401
    
    tokens = AuthService.create_tokens(user)
    return jsonify(tokens), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    
    tokens = AuthService.create_tokens(user)
    return jsonify(tokens), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'is_admin': user.is_admin,
        'qualification': user.qualification,
        'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None
    }), 200 