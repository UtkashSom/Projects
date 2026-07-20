from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import User, Admin, ParkingLot, ParkingSpot, SpotStatus, Reservation
from datetime import datetime
from werkzeug.security import generate_password_hash

engine = create_engine("sqlite:///parking_system.db")
Session = sessionmaker(bind=engine)
session = Session()

users = [
    User(name="Utkarsh", email="utk@gmail.com", password=generate_password_hash("123")),
    User(name="demo1", email="demo1@gmail.com", password=generate_password_hash("123")),
    User(name="demo2", email="demo2@gmail.com", password=generate_password_hash("123")),
]
session.add_all(users)
session.commit()

if not session.query(Admin).first():
    admin = Admin(username="admin@gmail.com", password=generate_password_hash("123"))
    session.add(admin)
    session.commit()

lots = [
    ParkingLot(prime_location_name="Downtown Parking", price=12.5, address="123 Dubai St", pin_code="00001", maximum_number_of_spots=5),
    ParkingLot(prime_location_name="Mall Parking", price=15.0, address="456 Mall Rd", pin_code="00002", maximum_number_of_spots=3),
]
session.add_all(lots)
session.commit()

spots = [
    ParkingSpot(lot_id=lots[0].id, status=SpotStatus.AVAILABLE),
    ParkingSpot(lot_id=lots[0].id, status=SpotStatus.OCCUPIED),
    ParkingSpot(lot_id=lots[0].id, status=SpotStatus.AVAILABLE),
    ParkingSpot(lot_id=lots[0].id, status=SpotStatus.AVAILABLE),
    ParkingSpot(lot_id=lots[0].id, status=SpotStatus.OCCUPIED),
    ParkingSpot(lot_id=lots[1].id, status=SpotStatus.AVAILABLE),
    ParkingSpot(lot_id=lots[1].id, status=SpotStatus.OCCUPIED),
    ParkingSpot(lot_id=lots[1].id, status=SpotStatus.AVAILABLE),
]
session.add_all(spots)
session.commit()

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
        leaving_timestamp=None, 
        parking_cost=None
    ),
]

users[0].spot_id = spots[1].id 
users[1].spot_id = spots[4].id 
users[2].spot_id = spots[6].id 

session.add_all(reservations)
session.commit()

print("Dummy data has been inserted.")
