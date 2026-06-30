import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if api_key and api_key != "your_api_key_here":
    client = genai.Client(api_key=api_key)
    try:
        models = [m.name for m in client.models.list()]
        print(f"AVAILABLE MODELS: {models}")
    except Exception as e:
        print(f"Error listing models: {e}")
else:
    print("API Key not found or invalid.")
