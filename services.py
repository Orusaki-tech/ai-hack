from sqlalchemy.orm import Session
import crud
import schemas
from typing import List, Optional

def get_all_market_data(db: Session) -> List[schemas.MarketData]:
    """
    Service layer function to retrieve all market data.
    In the future, business logic like filtering or analysis could be added here.
    """
    print("Fetching all market data records.")
    db_items = crud.get_all_market_data(db=db)
    return db_items

def get_market_data_by_id(db: Session, item_id: int) -> Optional[schemas.MarketData]:
    """
    Service layer function to retrieve a single market data item by its ID.
    """
    print(f"Fetching market data for ID: {item_id}")
    db_item = crud.get_market_data_by_id(db=db, item_id=item_id)
    return db_item