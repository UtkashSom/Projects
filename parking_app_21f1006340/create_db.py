from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Admin
from werkzeug.security import generate_password_hash

engine = create_engine('sqlite:///parking_system.db', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

if not session.query(Admin).first():
    default_admin = Admin(username="admin@gmail.com", password=generate_password_hash("123"))
    session.add(default_admin)
    session.commit()
    print("Admin user created.")
else:
    print("Admin user already exists.")

print("Database has been initialized.")
