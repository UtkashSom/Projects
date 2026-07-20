from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

login_manager = LoginManager()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config['SECRET_KEY'] = "21f1006340"
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///quiz_master.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    # Create database tables within app context
    with app.app_context():
        db.create_all()  

    return app