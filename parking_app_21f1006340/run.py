import os
from flask import Flask

from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp
from controllers.user_controller import user_bp

def create_app():
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')  # <-- Correct path
    app = Flask(__name__, template_folder=template_dir)
    app.secret_key = 'your_secret_key_here'

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)


