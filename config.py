import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
URL = "https://api.exchangerate-api.com/v4/latest/USD"