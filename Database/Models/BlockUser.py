from sqlalchemy import Column, Integer, String, DateTime
from ..base import Base

class BlockUser(Base):
    __tablename__="BlockUser"
    id=Column(Integer, primary_key=True)
    username=Column(String, nullable=False)
    user_menberid=Column(String, nullable=False)
    time=Column(DateTime, nullable=False)


