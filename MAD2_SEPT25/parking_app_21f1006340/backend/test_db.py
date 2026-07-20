from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Admin, ParkingLot, ParkingSpot, SpotStatus, Reservation

engine = create_engine('sqlite:///vehicle_parking.db')
Session = sessionmaker(bind=engine)
session = Session()

print("Admins:")
for admin in session.query(Admin).all():
    print(admin.id, admin.username)

print("\nUsers:")
for user in session.query(User).all():
    print(user.id, user.name, user.email)

print("\nParking Lots:")
for lot in session.query(ParkingLot).all():
    print(lot.id, lot.prime_location_name, lot.maximum_number_of_spots)

print("\nParking Spots:")
for spot in session.query(ParkingSpot).limit(5).all():
    print(spot.id, spot.lot_id, spot.status)

print("\nReservations:")
for res in session.query(Reservation).limit(5).all():
    print(res.id, res.user_id, res.spot_id, res.parking_timestamp, res.leaving_timestamp)

session.close()
