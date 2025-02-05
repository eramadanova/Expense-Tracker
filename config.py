import dotenv
import os
from utils import load_default_currency

dotenv.load_dotenv()

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("No API key provided!")

base_url = f"https://v6.exchangerate-api.com/v6/{API_KEY}"

default_currency = load_default_currency()