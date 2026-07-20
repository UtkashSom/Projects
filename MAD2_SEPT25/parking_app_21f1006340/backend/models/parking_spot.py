from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import Base
import enum

class SpotStatus(enum.Enum):
    AVAILABLE = "A"
    OCCUPIED = "O"

class ParkingSpot(Base):
    __tablename__ = 'parking_spots'

    id = Column(Integer, primary_key=True)
    lot_id = Column(Integer, ForeignKey('parking_lots.id'))
    status = Column(Enum(SpotStatus), default=SpotStatus.AVAILABLE)

    user = relationship("User", back_populates="spot", uselist=False)

    lot = relationship("ParkingLot", back_populates="spots")
    reservations = relationship("Reservation", back_populates="spot")
