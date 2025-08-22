from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import services
import schemas
from database import SessionLocal, create_db_and_tables

# Initialize DB tables when the API starts
create_db_and_tables()

app = FastAPI(
    title="PulsePrice AI API",
    description="An API to serve market price information collected by an independent AI ETL pipeline.",
    version="1.0.0"
)

# Dependency to get a DB session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/market-data/", response_model=List[schemas.MarketData])
def read_all_market_data(db: Session = Depends(get_db)):
    all_data = services.get_all_market_data(db=db)
    return all_data



@app.get("/market-data/{item_id}", response_model=schemas.MarketData)
def read_market_data_item(item_id: int, db: Session = Depends(get_db)):
    db_item = services.get_market_data_by_id(db=db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Market data item not found")
    return db_item