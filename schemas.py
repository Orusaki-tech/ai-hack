# file: schemas.py

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

# This is the base Pydantic model. It contains fields common to
# both creating and reading data.
class MarketDataBase(BaseModel):
    crop: str
    location: str
    price: str
    date_updated: str
    update_frequency: str
    source: Optional[str] = None

# This is the model that will be used when READING data from the API.
# It inherits from the base and adds the 'id' field, which is generated
# by the database.
class MarketData(MarketDataBase):
    id: int

    # This config class is crucial. It tells Pydantic to read the data
    # even if it is not a dict, but an ORM model (or any other arbitrary
    # object with attributes).
    class Config:
        from_attributes = True # For Pydantic v2. Use `orm_mode = True` for v1.