from .base import Base
from .user import User
from .admin import Admin
from .parking_lot import ParkingLot
from .parking_spot import ParkingSpot, SpotStatus
from .reservation import Reservation
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///vehicle_parking.db')
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
