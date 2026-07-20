from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    spot_id = Column(Integer, ForeignKey('parking_spots.id'))
    parking_timestamp = Column(DateTime, default=datetime.utcnow)
    leaving_timestamp = Column(DateTime)
    parking_cost = Column(Float)

    user = relationship("User", back_populates="reservations")
    spot = relationship("ParkingSpot", back_populates="reservations")
