from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import User, Admin, SessionLocal

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    session = SessionLocal()
    try:
        data = request.get_json()
        if not data:
            return jsonify({"msg": "No data provided"}), 400

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        missing = []
        if not name:
            missing.append("name")
        if not email:
            missing.append("email")
        if not password:
            missing.append("password")
        if missing:
            return jsonify({"msg": "Missing required fields: " + ", ".join(missing)}), 400

        existing = session.query(User).filter_by(email=email).first()
        if existing:
            return jsonify({"msg": "Email already registered"}), 409

        hashed = generate_password_hash(password)
        u = User(name=name, email=email, password=hashed)
        session.add(u)
        session.commit()

        return jsonify(
            {
                "msg": "User registered successfully",
                "user": {"id": u.id, "email": u.email, "name": u.name},
            }
        ), 201
    except Exception as e:
        session.rollback()
        return jsonify({"msg": "Internal server error", "error": str(e)}), 500
    finally:
        session.close()

@auth_bp.route("/login", methods=["POST"])
def login():
    session = SessionLocal()
    try:
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"msg": "Missing email or password"}), 400

        admin = session.query(Admin).filter_by(username=email).first()
        if admin and check_password_hash(admin.password, password):
            token = create_access_token(
                identity=str(admin.id),
                additional_claims={"is_admin": True, "email": admin.username}
            )
            return jsonify(
                {
                    "access_token": token,
                    "user": {
                        "id": admin.id,
                        "email": admin.username,
                        "name": "Admin",
                        "is_admin": True,
                    },
                }
            )

        user = session.query(User).filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"msg": "Invalid email or password"}), 401

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"is_admin": False, "email": user.email}
        )
        return jsonify(
            {
                "access_token": token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "is_admin": False,
                },
            }
        )
    except Exception as e:
        return jsonify({"msg": "Internal server error", "error": str(e)}), 500
    finally:
        session.close()
