from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Admin, ParkingLot, ParkingSpot, SpotStatus, Reservation
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

engine = create_engine("sqlite:///vehicle_parking.db")

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

print("Creating users...")
users = [
    User(name="Utkarsh", email="utksom@gmail.com", password=generate_password_hash("123")),
    User(name="Aditi", email="utksom27@gmail.com", password=generate_password_hash("123")),
    User(name="Mohit", email="utksom2709@gmail.com", password=generate_password_hash("123")),
    User(name="Riya", email="21f1006340@ds.study.iitm.ac.in", password=generate_password_hash("123")),
    User(name="Sadia", email="sadiakbar9122@gmail.com", password=generate_password_hash("123")),
]
session.add_all(users)
session.commit()
print(f"Created {len(users)} users")

print("Creating admin user...")
admin = Admin(username="admin@gmail.com", password=generate_password_hash("123"))
session.add(admin)
session.commit()
print("Admin user created")

print("Creating parking lots...")
lots = [
    ParkingLot(prime_location_name="Downtown Parking", price=20, address="123 Dubai St", pin_code="00001", maximum_number_of_spots=5),
    ParkingLot(prime_location_name="Mall Parking", price=25, address="456 Mall Rd", pin_code="00002", maximum_number_of_spots=3),
    ParkingLot(prime_location_name="Airport Parking", price=30, address="Airport Rd", pin_code="00003", maximum_number_of_spots=4),
]
session.add_all(lots)
session.commit()
print(f"Created {len(lots)} parking lots")

print("Creating parking spots...")
spots = []
spots_by_lot = {}

for lot in lots:
    lot_spots = []
    for _ in range(lot.maximum_number_of_spots):
        spot = ParkingSpot(lot_id=lot.id, status=SpotStatus.AVAILABLE)
        spots.append(spot)
        lot_spots.append(spot)
    spots_by_lot[lot.id] = lot_spots

session.add_all(spots)
session.commit()
print(f"Created {len(spots)} parking spots")

print("Creating reservations...")
reservations = []

utkarsh = users[0]
aditi = users[1]
mohit = users[2]
riya = users[3]
sadia = users[4]

downtown_spots = spots_by_lot[lots[0].id]
mall_spots = spots_by_lot[lots[1].id]
airport_spots = spots_by_lot[lots[2].id]

reservations.append(
    Reservation(
        spot_id=downtown_spots[0].id,
        user_id=utkarsh.id,
        parking_timestamp=datetime(2025, 10, 21, 9, 0),
        leaving_timestamp=datetime(2025, 10, 21, 12, 0),
        parking_cost=30.0,
    )
)

reservations.append(
    Reservation(
        spot_id=downtown_spots[0].id,
        user_id=utkarsh.id,
        parking_timestamp=datetime(2025, 10, 21, 9, 0),
        leaving_timestamp=datetime(2025, 10, 21, 12, 0),
        parking_cost=30.0,
    )
)

reservations.append(
    Reservation(
        spot_id=mall_spots[0].id,
        user_id=utkarsh.id,
        parking_timestamp=datetime(2025, 10, 22, 9, 0),
        leaving_timestamp=datetime(2025, 10, 22, 11, 0),
        parking_cost=25.0,
    )
)

reservations.append(
    Reservation(
        spot_id=downtown_spots[0].id,
        user_id=sadia.id,
        parking_timestamp=datetime(2025, 10, 21, 9, 0),
        leaving_timestamp=datetime(2025, 10, 21, 12, 0),
        parking_cost=30.0,
    )
)

reservations.append(
    Reservation(
        spot_id=mall_spots[0].id,
        user_id=sadia.id,
        parking_timestamp=datetime(2025, 10, 21, 9, 0),
        leaving_timestamp=datetime(2025, 10, 21, 11, 0),
        parking_cost=25.0,
    )
)

reservations.append(
    Reservation(
        spot_id=mall_spots[0].id,
        user_id=sadia.id,
        parking_timestamp=datetime(2025, 10, 22, 9, 0),
        leaving_timestamp=datetime(2025, 10, 22, 11, 0),
        parking_cost=25.0,
    )
)

reservations.append(
    Reservation(
        spot_id=mall_spots[0].id,
        user_id=aditi.id,
        parking_timestamp=datetime(2025, 10, 22, 14, 30),
        leaving_timestamp=datetime(2025, 10, 22, 16, 0),
        parking_cost=20.0,
    )
)

now = datetime(2025, 11, 23, 13, 0)

current_reservations = [
    Reservation(
        spot_id=downtown_spots[2].id,
        user_id=mohit.id,
        parking_timestamp=now - timedelta(hours=2),
        leaving_timestamp=None,
        parking_cost=None,
    ),
    Reservation(
        spot_id=mall_spots[1].id,
        user_id=riya.id,
        parking_timestamp=now - timedelta(hours=1, minutes=15),
        leaving_timestamp=None,
        parking_cost=None,
    ),
    Reservation(
        spot_id=airport_spots[0].id,
        user_id=sadia.id,
        parking_timestamp=now - timedelta(minutes=40),
        leaving_timestamp=None,
        parking_cost=None,
    ),
]

reservations.extend(current_reservations)

for res in current_reservations:
    spot = session.query(ParkingSpot).get(res.spot_id)
    user = session.query(User).get(res.user_id)
    if spot and user:
        spot.status = SpotStatus.OCCUPIED
        user.spot_id = spot.id

session.add_all(reservations)
session.commit()
print(f"Created {len(reservations)} reservations")

session.close()
print("✅ Dummy data inserted successfully.")
