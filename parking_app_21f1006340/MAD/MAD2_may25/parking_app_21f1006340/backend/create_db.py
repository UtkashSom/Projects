from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Admin
from werkzeug.security import generate_password_hash

engine = create_engine('sqlite:///vehicle_parking.db')
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

if not session.query(Admin).first():
    admin = Admin(
        username="admin@gmail.com",
        password=generate_password_hash("admin123")
    )
    session.add(admin)
    session.commit()

session.close()
