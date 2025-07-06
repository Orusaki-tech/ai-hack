# crud.py
from typing import List
from sqlalchemy.orm import Session
import models_1  # <--- Changed
import schemas # <--- Changed
from datetime import date

def save_market_data_list(db: Session, market_data_items: List[schemas.MarketDataBase]):
    """
    Takes a list of Pydantic MarketDatabaseBase objects, converts them to
    SQLAlchemy model instances, and saves them to the database in a single,
    efficient transaction.

    Args:
        db (Session): The active database session.
        market_data_items (List[schemas.MarketDatabaseBase]): A list of Pydantic
                                                              objects to be saved.

    Returns:
        List[models.MarketData]: The list of SQLAlchemy model instances that were saved.
    """
    print(f"--> [CRUD] Preparing to save a batch of {len(market_data_items)} items.")

    # 1. Use a list comprehension to convert all Pydantic objects into
    #    SQLAlchemy model instances. .model_dump() gets the data as a dictionary.
    db_objects = [models_1.MarketData(**item.model_dump()) for item in market_data_items]

    # 2. Use db.add_all() to add all the new objects to the session at once.
    #    This is much more efficient than adding them in a loop.
    db.add_all(db_objects)

    # 3. Commit the transaction to write all changes to the database.
    #    This happens only once for the entire batch.
    db.commit()

    print(f"--> [CRUD] Successfully committed {len(db_objects)} items to the database.")

    # Return the list of created database objects.
    # Note: Their IDs are now populated from the database.
    return db_objects

# You can also keep a function to read the data to verify it
def get_all_market_data(db: Session):
    """
    Retrieves all market data records from the database.
    """
    return db.query(models_1.MarketData).all()

# def get_all_market_data(db: Session):
#     """
#     Retrieves all market data items from the database.
#     """
#     return db.query(models.MarketData).all()