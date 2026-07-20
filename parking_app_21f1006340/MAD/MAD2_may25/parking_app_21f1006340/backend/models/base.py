from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine(
    'sqlite:///vehicle_parking.db',
    echo=True,
    connect_args={"check_same_thread": False}
)

SessionLocal = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
