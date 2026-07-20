from models.base import Base, engine
from models.user import User
from models.admin import Admin
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.reservation import Reservation

Base.metadata.create_all(bind=engine)

print("Tables have been created.")