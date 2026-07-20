from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import User, Admin, SessionLocal

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    session = SessionLocal()
    try:
        print("\n=== New Registration Request ===")
        print(f"Headers: {dict(request.headers)}")
        print(f"Content-Type: {request.content_type}")
        
        data = request.get_json()
        if not data:
            print("Error: No JSON data received")
            return jsonify({"msg": "No data provided"}), 400
            
        print(f"Received data: {data}")
        
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        missing_fields = []
        if not name:
            missing_fields.append('name')
        if not email:
            missing_fields.append('email')
        if not password:
            missing_fields.append('password')
            
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            print(f"Validation error: {error_msg}")
            return jsonify({"msg": error_msg}), 400

        existing_user = session.query(User).filter_by(email=email).first()
        if existing_user:
            print(f"Registration failed: Email {email} already registered")
            return jsonify({"msg": "Email already registered"}), 409

        try:
            hashed_password = generate_password_hash(password)
            new_user = User(name=name, email=email, password=hashed_password)
            session.add(new_user)
            session.commit()
            print(f"User {email} registered successfully")
            return jsonify({
                "msg": "User registered successfully",
                "user": {"id": new_user.id, "email": new_user.email, "name": new_user.name}
            }), 201
            
        except Exception as e:
            session.rollback()
            print(f"Error during user creation: {str(e)}")
            return jsonify({"msg": "Error creating user", "error": str(e)}), 500
            
    except Exception as e:
        session.rollback()
        print(f"Unexpected error in register endpoint: {str(e)}")
        return jsonify({"msg": "Internal server error", "error": str(e)}), 500
        
    finally:
        session.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    session = SessionLocal()
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        print(f"Login attempt: {username} / {password}")

        if not username or not password:
            return jsonify({"msg": "Missing username or password"}), 400

        admin = session.query(Admin).filter_by(username=username).first()
        if admin:
            print("Admin found in DB")
            if check_password_hash(admin.password, password):
                print("Admin password matched")
                access_token = create_access_token(identity={"id": admin.id, "role": "admin", "username": admin.username})
                return jsonify(access_token=access_token, role="admin")
            else:
                print("Admin password incorrect")

        user = session.query(User).filter_by(email=username).first()
        if user:
            print("User found in DB")
            if check_password_hash(user.password, password):
                print("User password matched")
                access_token = create_access_token(identity={"id": user.id, "role": "user", "email": user.email})
                return jsonify(access_token=access_token, role="user")
            else:
                print("User password incorrect")

        return jsonify({"msg": "Bad username or password"}), 401
    except Exception as e:
        import logging
        logging.exception("Error during login")
        return jsonify({"msg": "Internal server error", "error": str(e)}), 50
