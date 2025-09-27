from sqlalchemy import Column, Integer, String, DateTime
from ..base import Base

class Posted(Base):
    __tablename__="Posted"
    id=Column(Integer, primary_key=True)
    username=Column(String, nullable=False)
    user_menberid=Column(String, nullable=False)
    created_at=Column(DateTime, nullable=False)
