# To run this code you need to install the following dependencies:
# pip install google-genai


import os
from google import genai
from datetime import date

# Import our new modules
from database import SessionLocal, create_db_and_tables
import crud
import schemas



import json
from google import genai
from google.genai import types
import pydantic

from google.genai.types import HarmCategory, HarmBlockThreshold

from crud import get_all_market_data, save_market_data_list
import crud
from database import SessionLocal, create_db_and_tables
from schemas import  MarketData, MarketDataBase
import schemas


# It's good practice to create the tables at the start of the application
print("Initializing database and creating tables if they don't exist...")
create_db_and_tables()
print("Database initialized.")


safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

GEMINI_API_KEY="AIzaSyBvaH2i7Ou7T1is3K8DIY9xkkQ4eS0MlQg"




client = genai.Client(
        api_key=GEMINI_API_KEY,
    )

model = "gemini-2.5-pro"
contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""You are a hyper-precise data extraction agent. Your primary function is to convert unstructured information from websites into a strictly validated JSON format that can be directly ingested by a database without any errors. Failure to adhere to the specified schema is a failure of your primary function.
You will search the websites (https://kamis.kilimo.go.ke/, https://ncx.com.ng/) for price information on maize and potatoes.
Your output MUST be a valid JSON array of objects. Each object in the array MUST strictly conform to the following Pydantic schema. Pay extremely close attention to the data type of each field.
class MarketDataBase(BaseModel):
    crop: str
    location: str
    price: str
    date_updated: str
    update_frequency: str
    source: Optional[str] = None
Field-Specific Rules You Must Follow:
 crop (string): The name of the crop.
 location (string): The full market location. You must expand all abbreviations (e.g., 'KAN' becomes 'Kano, Nigeria').
 price (string): The price as a string. You must include the currency and the unit (e.g., "KES 4,900 per 90kg bag", not 4900).
 date_updated (string): The date and time the data was updated. This MUST be a string in the exact ISO 8601 format: YYYY-MM-DDTHH:MM:SS. Do not use any other format.
 update_frequency (string): This field MUST contain one of two exact values: "Daily" or "Weekly". Use the title case.
 source (Optional[str]): The source URL.
 Here is a perfect example of a single object:

{
  "crop": "Maize",
  "location": "Nairobi, Kenya",
  "price": "KES 5,050 per 90kg bag",
  "date_updated": "2023-10-28T10:15:00",
  "update_frequency": "Daily",
  "source": "https://kamis.kilimo.go.ke/"
}
                                     
Before providing your final response, perform a final check on the generated JSON. Verify that it is a valid JSON array and that every single object within it complies with all the field-specific rules and the Pydantic schema provided. Correct any errors you find."""),],
        )
    ]
tools = [
        types.Tool(url_context=types.UrlContext()),
    ]
generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
        tools=tools,
        response_mime_type="text/plain",
        response_schema=MarketDataBase,
    )

response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,)

print(response)
print(response.text)        

# parsed_data = json.loads(response.text)
# parsed_data = json.loads(parsed_data)

# print(parsed_data)

try:
    start_index = response.text.find('[')
    if start_index == -1:
        start_index = response.text.find('{')

    end_index = response.text.rfind(']')
    if end_index == -1:
        end_index = response.text.rfind('}')

    if start_index != -1 and end_index != -1:
        # Slice the string to get ONLY the pure JSON part
        clean_json_string = response.text[start_index : end_index + 1]
    else:
        # If we can't find it, raise an error
        raise ValueError("Valid JSON array/object not found in the model's text response.")

    # 3. Now, parse the CLEANED string using json.loads()
    parsed_data = json.loads(clean_json_string)

    # 4. Print the final Python object (list of dictionaries) to verify
    print("\n--- Successfully Parsed Python Data ---")
    print(parsed_data)

    # Now you can use 'parsed_data' to create your Pydantic models and save to the DB
    # ... your database saving logic would go here ...

except (json.JSONDecodeError, ValueError) as e:
    print(f"\n❌ ERROR: Failed to parse JSON from the model's response. Reason: {e}")


# market_data_list= parsed_data.parsed

# print(market_data_list)

try:
    # Step 2: Loop through the parsed data and validate each item individually
    market_data_list = []
    print("\n--- Validating and converting raw data to Pydantic models ---")

    for i, item in enumerate(parsed_data):  # Using enumerate to get the index for error reporting
        try:
            # Pydantic will automatically map all keys from the 'item' dictionary
        # to the fields in the MarketDataBase schema. It's cleaner and safer.
            pydantic_model = schemas.MarketDataBase(**item)
            market_data_list.append(pydantic_model)

        # FIX 2: Catch validation errors for a SINGLE item
        except pydantic.ValidationError as e:
            print(f"⚠️  Skipping record #{i+1} due to validation error.")
            print(f"   Problematic Data: {item}")
            print(f"   Validation Error: {e}\n")
            # The loop will now continue to the next item instead of crashing

    print(f"✅ Successfully converted {len(market_data_list)} valid records.")

    # Step 3: Pass the list of VALID Pydantic objects to the database function.
    if market_data_list:
        db = SessionLocal() # <--- Create a new database session
        try:
            # Pass BOTH the database session and the list of items
            crud.save_market_data_list(db=db, market_data_items=market_data_list)
            print("✅ Data successfully saved to the database.")
        finally:
            db.close() # <--- Ensure the session is closed
    else:
        print("No valid data was found to save.")

    # Step 4: Show the results
    # Step 4: VERIFY BY PRINTING FROM DATABASE
    print("\n--- Verifying data from the database ---")
    db = SessionLocal()  # <--- 1. Create a new database session
    try:
        # Pass the session 'db' as an argument to the function
        all_items = crud.get_all_market_data(db=db) # <--- 2. Use the session

        if not all_items:
            print("No items found in the database.")
        for item in all_items:
            # Note: item.date_updated will now be a datetime object
            print(f"  [DB_RECORD] ID: {item.id}, Crop: {item.crop}, Location: {item.location}, Price: {item.price}, Date: {item.date_updated.strftime('%Y-%m-%d %H:%M:%S')}")

    finally:
        db.close() # <--- 3. Close the session when you're done



except json.JSONDecodeError as e:
    print(f"❌ JSON DECODE ERROR: The model returned an invalid JSON string. Error: {e}")
    # No need to print raw_text again here, it's already printed above.
except Exception as e:
    print(f"\nAn error occurred during processing: {e}")








# # --- Main Logic with Save and Print Functions ---

# def save_prices_to_db(market_data_list: list[schemas.MarketDataBase]):
#     """
#     This is the save function. It iterates through a list of Pydantic objects
#     and saves each one to the database.
#     """
#     print("\n--- Starting to save data to the database ---")
#     # Get a database session
#     db = SessionLocal()
#     try:
#         for item in market_data_list:
#             crud.save_market_data_list(db=db, item=item)
#             print(f"  [SAVED] Crop: {item.crop}, Price: {item.price}")
#     finally:
#         db.close() # Always close the session
#     print("--- Finished saving data ---\n")



# def show_data_from_db():
#     """
#     This function retrieves all records from the database and prints them
#     to show that the data has been successfully saved.
#     """
#     print("--- Retrieving all records from the database ---")
#     db = SessionLocal()
#     try:
#         all_items = crud.get_all_market_data(db=db)
#         if not all_items:
#             print("  No data found in the database.")
#             return

#         for item in all_items:
#             # We can use the Pydantic schema to validate the data coming from the DB
#             # The `from_attributes=True` in your schema's Config makes this work
#             pydantic_item = schemas.MarketDatabase.from_orm(item)
#             print(f"  [DB_RECORD] ID: {pydantic_item.id}, Crop: {pydantic_item.crop}, Price: {pydantic_item.price}, Date: {pydantic_item.date_updated}")
#     finally:
#         db.close()
#     print("--- Finished retrieving data ---")

