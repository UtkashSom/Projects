from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from .base import Base

class ParkingLot(Base):
    __tablename__ = 'parking_lots'

    id = Column(Integer, primary_key=True)
    prime_location_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    pin_code = Column(String, nullable=False)
    maximum_number_of_spots = Column(Integer, nullable=False)

    spots = relationship("ParkingSpot", back_populates="lot", cascade="all, delete-orphan")
