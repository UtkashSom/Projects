from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    spot_id = Column(Integer, ForeignKey('parking_spots.id'), nullable=True)
    spot = relationship("ParkingSpot", back_populates="user", uselist=False)

    reservations = relationship("Reservation", back_populates="user")
