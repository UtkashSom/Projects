from app import create_app, db
from app.models import User
from datetime import datetime

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin exists
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            # Create admin user
            admin = User(
                email='admin@quizmaster.com',
                full_name='Quiz Master Admin',
                is_admin=True,
                date_of_birth=datetime.strptime('1990-01-01', '%Y-%m-%d')
            )
            admin.set_password('admin123')  # Set a secure password in production
            db.session.add(admin)
            db.session.commit()
            print('Admin user created successfully!')
        else:
            print('Admin user already exists!')

if __name__ == '__main__':
    init_db() 