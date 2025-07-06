# In genai.py

import os
import json
from google import genai
import pydantic

# Import your project modules
import schemas
import crud
from database import SessionLocal, create_db_and_tables

# --- 1. SETUP ---
# Initialize the database and create tables if they don't exist
print("Initializing database...")
create_db_and_tables()

# Configure the Generative AI client

    # Use environment variables for API keys in real projects
    # from dotenv import load_dotenv
    # load_dotenv()

GEMINI_API_KEY="AIzaSyCj7-hhuD72mHrJNwtV5ZQmTvT3Wg620Os"

client = genai.Client(
        api_key=GEMINI_API_KEY,
    )

# --- 2. CONFIGURE THE MODEL FOR JSON MODE ---
# This is where we tell the model to use your schema and return JSON
generation_config = genai.GenerationConfig(
    response_mime_type="application/json",
    response_schema=schemas.MarketDataResponse  # <-- This activates JSON Mode!
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest", # Using a more powerful model is good for complex tasks
    generation_config=generation_config,
    # Safety settings are still important to prevent the model from refusing to answer
    safety_settings={
        'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
        'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
        'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
        'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
    }
)

# --- 3. DEFINE THE PROMPT ---
# This is your detailed prompt, directly in the code.
prompt = """
You are an agent that provides price information to farmers who are ready to harvest and want to find the markets to sell their produce to at the highest price.
You search though a list of websites given below (https://kamis.kilimo.go.ke/, https://ncx.com.ng/) that provide price information about maize and potatoes in markets all over the region and the continent.
You extract the price, crop, date the information was last updated, how often it is updated (either daily or weekly), and the location of the market ONLY.
You present your results in JSON so that the results can be saved to a database.

Ensure the results follow this schema:
"crop": "Maize White",
"location": "Kaduna, Nigeria",
"price": "NGN 475/KG",
"date_updated": "2025-07-01",
"update_frequency": "Daily",
"source": "https://ncx.com.ng/"

Ensure you extract the full locations of markets from the websites, expanding any abbreviations (e.g., expand 'KAN' to 'Kano, Nigeria').
"""

# --- 4. GENERATE CONTENT AND SAVE TO DATABASE ---
print("\nGenerating market data from AI...")
try:
    # Call the model with the prompt
    response = model.generate_content(prompt)

    # With JSON mode, response.text is guaranteed to be a valid JSON string.
    # No more manual cleaning is needed!
    print("--- AI Response (Pure JSON) ---")
    print(response.text)
    
    # Parse the guaranteed-valid JSON string
    parsed_json = json.loads(response.text)
    
    # Extract the list of market data dictionaries
    market_data_dicts = parsed_json['market_data']

    # Convert the list of dictionaries into a list of Pydantic objects
    # This step validates the data against our schema one last time.
    market_data_list = [schemas.MarketData(**item) for item in market_data_dicts]
    print(f"\n✅ Successfully parsed and validated {len(market_data_list)} records.")

    # Save the validated data to the database
    if market_data_list:
        db = SessionLocal()
        try:
            crud.save_market_data_list(db=db, market_data_items=market_data_list)
            print("✅ Data successfully saved to the database.")
        finally:
            db.close()
    else:
        print("⚠️ No market data returned by the model.")

    # --- 5. VERIFY BY PRINTING FROM DATABASE ---
    print("\n--- Verifying data from the database ---")
    db = SessionLocal()
    try:
        all_items = crud.get_all_market_data(db=db)
        if not all_items:
            print("No items found in the database.")
        for item in all_items:
            print(f"  [DB_RECORD] ID: {item.id}, Crop: {item.crop}, Location: {item.location}, Price: {item.price}, Source: {item.source}")
    finally:
        db.close()

except Exception as e:
    print(f"\n❌ An error occurred: {e}")