from sqlalchemy import Column, Integer, String
from ..base import Base

class Bookingcheck(Base):
    __tablename__="BookingCheck"
    id=Column(Integer, primary_key=True)
    memberid=Column(String, nullable=False)

    