import os
import google.generativeai as genai
from dotenv import load_dotenv



def configure_genai_client():
    """
    Configures and returns the Google Generative AI client using an API key
    from environment variables.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

    genai.configure(api_key=api_key)
    return genai

def get_market_data_extraction_prompt() -> str:
    """
    Returns the detailed, structured prompt for market data extraction.
    """
    prompt = """
You are an agent that provides price information to farmers who are ready to harvest and want to find the markets to sell their produce to at the highest price.
You search though a list of websites given below (https://kamis.kilimo.go.ke/, https://ncx.com.ng/) that provide price information about maize and potatoes in markets all over the region and the continent.
You extract the price, crop, date the information was last updated, how often it is updated (either daily or weekly), the location of the market, and the source URL ONLY.
Your output MUST be a valid JSON array of objects.

Ensure each object in the array strictly conforms to this example structure:
{
  "crop": "Maize White",
  "location": "Kaduna, Nigeria",
  "price": "NGN 475/KG",
  "date_updated": "2025-07-01T10:30:00",
  "update_frequency": "Daily",
  "source": "https://ncx.com.ng/"
}

- For `date_updated`, you MUST use the ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
- You MUST expand any location abbreviations (e.g., expand 'KAN' to 'Kano, Nigeria').
- Ensure your entire response is ONLY the JSON array, with no other text before or after it.
"""
    return prompt



def fetch_ai_market_data() -> str:
    """
    Initializes the AI model, sends the data extraction prompt, and returns
    the raw JSON string response from the AI.
    """

    client = configure_genai_client()

    generation_config = genai.GenerationConfig(
        response_mime_type="application/json",
    )

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config=generation_config,
      
    )

    prompt = get_market_data_extraction_prompt()

    print("Sending prompt to Gemini model...")
    response = model.generate_content(prompt)

    if not response.text:
        raise Exception("model returned an empty response.")
    
    print(" Successfully received JSON response from model.")
    return response.text