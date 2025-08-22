import json
from pydantic import ValidationError, BaseModel
from typing import List, Dict, Any
import crud
import schemas
from database import SessionLocal, create_db_and_tables
from google_genai_logic import fetch_ai_market_data





def validate_and_transform_market_data(
    raw_data: List[Dict[str, Any]]
) -> List[schemas.MarketDataBase]:
    """
    Takes a list of raw data dictionaries, validates them against the
    MarketDataBase schema, and transforms them into Pydantic models.
    This is the "Transform" step of the ETL process.
    """
    validated_data_list = []
    print("\n--Validating and transforming raw data... ---")

    for i, item_dict in enumerate(raw_data):
        try:
            pydantic_model = schemas.MarketDataBase(**item_dict)
            validated_data_list.append(pydantic_model)
        except ValidationError as e:
            print(f"skipping record #{i+1} due to validation error.")
            print(f"   Problematic Data: {item_dict}")
            print(f"   Validation Error: {e}\n")

    print(f"Successfully converted {len(validated_data_list)} valid records.")
    return validated_data_list
# ----------------------------------------------------

def run_etl_pipeline():
    """
    The main ETL function that extracts, transforms, and loads the market data.
    """
    print(" Starting AI data extraction pipeline ---")
    try:
        # 1. EXTRACT
        print("fetching data from Generative AI...")
        raw_json_string = fetch_ai_market_data()
        
        if raw_json_string.strip().startswith("```json"):
            raw_json_string = raw_json_string.strip()[7:-4]
            
        
        parsed_data = json.loads(raw_json_string, strict=False)

        # 2. TRANSFORM: Call the local transformation function
        market_data_list = validate_and_transform_market_data(raw_data=parsed_data)

        # 3. LOAD: Save the validated data to the database using the clean CRUD layer
        if market_data_list:
            print(f"Loading {len(market_data_list)} records into the database...")
            db = SessionLocal()
            try:
                # The CRUD layer is now only responsible for saving
                crud.save_market_data_list(db=db, market_data_items=market_data_list)
                print("Data successfully loaded.")
            finally:
                db.close()
        else:
            print("No valid records were found to save.")

    except (ValidationError, json.JSONDecodeError) as e:
        print(f"A data validation or parsing error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during the pipeline: {e}")


if __name__ == "__main__":
    print("Initializing database for ETL process...")
    create_db_and_tables()
    run_etl_pipeline()