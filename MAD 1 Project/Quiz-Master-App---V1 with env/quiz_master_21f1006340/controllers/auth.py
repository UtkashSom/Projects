from quiz_master_21f1006340 import db
from flask import render_template, redirect, flash, url_for
from quiz_master_21f1006340.models.user import User
from quiz_master_21f1006340.forms import RegisterForm, LoginForm
from flask_login import login_user, login_required, logout_user
from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
                    username=form.username.data,
                    fullname=form.fullname.data,
                    qualification=form.qualification.data,
                    dob=form.dob.data
                    )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You were successfully registered', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form = form)

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('You were successfully logged in', 'success')

            if user.username == "admin@iitm.ac.in":
                return redirect(url_for('admin.admin_dashboard'))  
            else:
                return redirect(url_for('users.dashboard'))  
            
        else:
            flash('Please check the username and password combo', 'error')
    return render_template("login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash('User logged out', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route("/admin/login", methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username="admin@iitm.ac.in").first()
        if user and user.username == form.username.data and user.check_password(form.password.data):
            login_user(user)
            flash("Successfully logged in as Quiz Master Admin!", 'success')
            return redirect(url_for('admin_dashboard')) 
        else:
            flash("Incorrect details! Access denied", 'warning')
    return render_template("admin/login.html", form=form)