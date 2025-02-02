"""Declare models and relationships."""
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from database import engine

Base = declarative_base()



class UserProfile(Base):
    """User Profile"""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    email = Column(String(255), nullable=False, unique=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    season = Column(String(255), nullable=True)
    team = Column(String(255), nullable=True)
    player = Column(String(255), nullable=True)
    timestamp = Column(DateTime, server_default=func.now())  # When the profile was created
    is_subscribed = Column(Integer, nullable=False, default=0)  # 1 for subscribed, 0 for not subscribed

    def __repr__(self):
        return f"<UserProfile id={self.id}, email={self.email}, first_name={self.first_name}, last_name={self.last_name}, season={self.season}, team={self.team}, player={self.player}, timestamp={self.timestamp}, is_subscribed={self.is_subscribed}>"

Base.metadata.create_all(engine)