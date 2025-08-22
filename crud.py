
from typing import List, Optional
from sqlalchemy.orm import Session
import models
import schemas

# --- WRITE Operations (Used by the ETL Pipeline) ---

def save_market_data_list(db: Session, market_data_items: List[schemas.MarketDataBase]) -> List[models.MarketData]:
    """
    Takes a list of Pydantic MarketDataBase objects, converts them to
    SQLAlchemy model instances, and saves them to the database in a single
    efficient transaction.
    """
    print(f" Preparing to save a batch of {len(market_data_items)} items.")
    
    # This is a data mapping step, perfectly suitable for the DAL
    db_objects = [models.MarketData(**item.model_dump()) for item in market_data_items]

    db.add_all(db_objects)
    db.commit()

    print(f"Successfully committed {len(db_objects)} items to the database.")
    return db_objects


# --- READ Operations (Used by the Service Layer) ---

def get_all_market_data(db: Session) -> List[models.MarketData]:
    """
    Retrieves all market data records from the database.
    """
    print("Querying all market data records.")
    return db.query(models.MarketData).all()


def get_market_data_by_id(db: Session, item_id: int) -> Optional[models.MarketData]:
    """
    Retrieves a single market data record from the database by its ID.
    """
    print(f"Querying for market data with ID: {item_id}.")
    return db.query(models.MarketData).filter(models.MarketData.id == item_id).first()