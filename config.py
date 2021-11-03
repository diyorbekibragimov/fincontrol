import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
URL = os.getenv('EXCHANGE_URL')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH") + f"/{BOT_TOKEN}"
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT'))

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

imported = {
    'BOT_TOKEN':BOT_TOKEN, 
    'EXCHAGE_URL': URL,
    'HEROKU_APP_NAME': HEROKU_APP_NAME,
    'WEBAPP_PORT': WEBAPP_PORT
}

for (k, v) in imported.items():
    if not v:
        print(f"You have forgotten to set {k}")