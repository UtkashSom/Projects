from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

from models.base import engine
from models.user import User
from models.admin import Admin

auth_bp = Blueprint('auth', __name__)

Session = sessionmaker(bind=engine)

def check_if_admin(email_address):
    db_session = Session()
    admin_record = db_session.query(Admin).filter_by(username=email_address).first()
    db_session.close()
    return admin_record is not None

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_name = request.form['name']
        user_email = request.form['email']
        user_password = request.form['password']

        db_session = Session()
        user_exists = db_session.query(User).filter_by(email=user_email).first()
        if user_exists:
            flash('This email is already in use.', 'error')
            db_session.close()
            return redirect(url_for('auth.register'))

        hashed_pw = generate_password_hash(user_password)
        new_user = User(name=user_name, email=user_email, password=hashed_pw)
        db_session.add(new_user)
        db_session.commit()
        db_session.close()

        flash('Successfully registered! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['password']

        db_session = Session()

        admin = db_session.query(Admin).filter_by(username=user_email).first()

        print(f"Attempting admin login with email: {user_email}")
        print(f"Admin record found? {'Yes' if admin else 'No'}")
        if admin:
            print(f"Stored admin password hash: {admin.password}")
            print(f"Password verification: {check_password_hash(admin.password, user_password)}")

        if admin and check_password_hash(admin.password, user_password):
            session['user_type'] = 'admin'
            session['username'] = user_email
            db_session.close()
            return redirect(url_for('admin.dashboard'))

        user = db_session.query(User).filter_by(email=user_email).first()

        print(f"Attempting user login with email: {user_email}")
        print(f"User record found? {'Yes' if user else 'No'}")
        if user:
            print(f"Stored user password hash: {user.password}")
            print(f"Password verification: {check_password_hash(user.password, user_password)}")

        if user and check_password_hash(user.password, user_password):
            session['user_type'] = 'user'
            session['user_id'] = user.id
            session['username'] = user.name
            db_session.close()
            return redirect(url_for('user.user_dashboard'))

        flash('Incorrect email or password.', 'error')
        db_session.close()
        return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
