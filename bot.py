from aiogram import executor
from dispatcher import dp
import handlers
import os, config

from db import BotDB
BotDB = BotDB('fincontrol.db')

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))
    executor.start_webhook(listen="0.0.0.0", 
                            port=int(PORT),
                            url_path=config.BOT_TOKEN)
    executor.bot.setWebhook("https://control-finance-bot.herokuapp.com/" + config.BOT_TOKEN)