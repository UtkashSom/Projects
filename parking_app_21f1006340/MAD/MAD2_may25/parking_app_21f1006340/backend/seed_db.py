from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Admin, ParkingLot, ParkingSpot, SpotStatus, Reservation
from werkzeug.security import generate_password_hash
from datetime import datetime

engine = create_engine('sqlite:///vehicle_parking.db')
Session = sessionmaker(bind=engine)
session = Session()

if not session.query(User).first():
    users = [
        User(name="Utkarsh", email="utkarsh@example.com", password=generate_password_hash("password123")),
        User(name="Aditi", email="aditi@example.com", password=generate_password_hash("securepass")),
        User(name="Mohit", email="mohit@example.com", password=generate_password_hash("mypassword")),
    ]
    session.add_all(users)
    session.commit()
else:
    users = session.query(User).all()

if not session.query(Admin).first():
    admin = Admin(username="admin@gmail.com", password=generate_password_hash("admin123"))
    session.add(admin)
    session.commit()

if not session.query(ParkingLot).first():
    lots = [
        ParkingLot(prime_location_name="Downtown Parking", price=12.5, address="123 Dubai St", pin_code="00001", maximum_number_of_spots=5),
        ParkingLot(prime_location_name="Mall Parking", price=15.0, address="456 Mall Rd", pin_code="00002", maximum_number_of_spots=3),
    ]
    session.add_all(lots)
    session.commit()
else:
    lots = session.query(ParkingLot).all()

if not session.query(ParkingSpot).first():
    spots = []
    for lot in lots:
        for _ in range(lot.maximum_number_of_spots):
            spots.append(ParkingSpot(lot_id=lot.id, status=SpotStatus.AVAILABLE))
    session.add_all(spots)
    session.commit()
else:
    spots = session.query(ParkingSpot).all()

if not session.query(Reservation).first():
    reservations = [
        Reservation(
            spot_id=spots[1].id,
            user_id=users[0].id,
            parking_timestamp=datetime(2025, 6, 23, 10, 0),
            leaving_timestamp=datetime(2025, 6, 23, 12, 0),
            parking_cost=25.0
        ),
        Reservation(
            spot_id=spots[4].id,
            user_id=users[1].id,
            parking_timestamp=datetime(2025, 6, 22, 14, 30),
            leaving_timestamp=datetime(2025, 6, 22, 15, 45),
            parking_cost=15.0
        ),
        Reservation(
            spot_id=spots[6].id,
            user_id=users[2].id,
            parking_timestamp=datetime(2025, 6, 21, 9, 0),
            leaving_timestamp=None,  # Still parked
            parking_cost=None
        ),
    ]
    session.add_all(reservations)
    session.commit()

session.close()

print("✅ Dummy data inserted successfully.")
