from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models import User
from flask import jsonify

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                
                if not identity or not identity.get('is_admin'):
                    return jsonify({"msg": "Admin access required"}), 403
                    
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({"msg": "Invalid or expired token"}), 401
        return decorator
    return wrapper

def user_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                identity = get_jwt_identity()
                
                if not identity:
                    return jsonify({"msg": "User access required"}), 403
                    
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({"msg": "Invalid or expired token"}), 401
        return decorator
    return wrapper 