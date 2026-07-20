from quiz_master_21f1006340 import create_app, db, login_manager
from flask import render_template, request
from quiz_master_21f1006340.models.question import Question
from quiz_master_21f1006340.models.quiz import Quiz
from quiz_master_21f1006340.models.subject import Subject
from quiz_master_21f1006340.models.user import User
from flask_login import current_user
from quiz_master_21f1006340.seed import seed_database
from quiz_master_21f1006340.controllers.auth import auth_bp
from quiz_master_21f1006340.controllers.users_controller import users_bp
from quiz_master_21f1006340.controllers.admin_controller import admin_bp

app = create_app()

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(admin_bp)

@login_manager.user_loader
def load_user(user_id):
    with db.session() as session:  # Create a session
        return session.get(User, user_id)

def ensure_admin():
    with app.app_context():  # Ensures correct database access
        admin_user = User.query.filter_by(username="admin@iitm.ac.in").first()
        if admin_user and not admin_user.is_admin:
            admin_user.is_admin = True
            db.session.commit()
            print("Admin rights granted!")
        else:
            print("Admin already set or user does not exist.")

@app.cli.command('db-create')
def create_db():
    db.create_all()
    admin = User.query.filter_by(username="admin@iitm.ac.in").first()
    if not admin:
        admin = User(
            username = "admin@iitm.ac.in",
            fullname = "Admin of Quiz Master"
        )
        admin.set_password("123456")
        db.session.add(admin)
        db.session.commit()
        print("Admin account initiated")
    else:
        print("Admin already present")
    print("Database creation successful")

@app.cli.command('db-seed')
def seed_db():
    seed_database()
    print("Seed database initiated")

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('search_results.html', query=query, users=[], subjects=[], quizzes=[], questions=[], is_admin=False)

    # Debugging: Check if `current_user` is recognized
    print("Current User:", current_user.username if current_user.is_authenticated else "Not Authenticated")

    is_admin = current_user.is_authenticated and current_user.username == "admin@iitm.ac.in"
    print("Admin Status:", is_admin)  # Debugging line

    # Search for users (Admins only)
    users = User.query.filter(User.username.ilike(f"%{query}%")).all() if is_admin else []

    # Search for subjects
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()

    # Search for quizzes
    quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{query}%")).all()

    # Search for questions (Admins only)
    questions = Question.query.filter(Question.question_statement.ilike(f"%{query}%")).all() if is_admin else []

    return render_template(
        'search_results.html',
        query=query,
        users=users,
        subjects=subjects,
        quizzes=quizzes,
        questions=questions,
        is_admin=is_admin  # Ensure this is passed correctly
    )


if __name__ == "__main__":
    app.run(debug=True)
    