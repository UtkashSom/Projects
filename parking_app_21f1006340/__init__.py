from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key_here'

    from app.controllers.auth_controller import auth_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.user_controller import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    return app
