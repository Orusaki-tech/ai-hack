# models.py
from sqlalchemy import Column, Integer, String, Date
from database import Base # <--- Changed

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    crop = Column(String, index=True)
    price = Column(String)
    date_updated = Column(Date)
    location = Column(String, index=True)
    update_frequency = Column(String, nullable=True)