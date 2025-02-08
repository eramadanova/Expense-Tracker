"""
Configuration settings for the application.
Loads environment variables and sets up API-related configurations.
"""

import os
import dotenv

dotenv.load_dotenv()

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("No API key provided!")

BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}"

DEFAULT_CURRENCY = ''
