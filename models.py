from sqlalchemy import Column, Integer, String, DateTime
from database import Base 

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    crop = Column(String, index=True)
    price = Column(String)
    date_updated = Column(DateTime) 
    location = Column(String, index=True)
    update_frequency = Column(String, nullable=True)
    source = Column(String, nullable=True)