import logging, asyncio

from aiogram import (Bot, Dispatcher)
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from filters import (IsOwnerFilter, IsAdminFilter, MemberCanRestrictFilter)
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.executor import start_webhook
from config import (BOT_TOKEN, WEBHOOK_URL, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_PATH)
from db import BotDB

# init
BotDB = BotDB('fincontrol.db')
loop = asyncio.get_event_loop()
bot = Bot(token=BOT_TOKEN, parse_mode="HTML", loop=loop)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

# activate filters
dp.filters_factory.bind(IsOwnerFilter)
dp.filters_factory.bind(IsAdminFilter)
dp.filters_factory.bind(MemberCanRestrictFilter)

async def on_startup(dp):
    logging.warning(
        'Starting connection...')
        
    webhook = await bot.get_webhook_info()

    # If URL is bad
    if webhook.url != WEBHOOK_URL:
        # If URL doesnt match current - remove webhook
        if not webhook.url:
            logging.warning("Bad URL")
            await bot.delete_webhook()

        # Set new URL for webhook
        await bot.set_webhook(WEBHOOK_URL)
    import handlers.users.actions

async def on_shutdown(dp):
    logging.warning('Goodbye! Shutting down webhook connection')
    await bot.delete_webhook()

    # Close Redis connection.
    await dp.storage.close()
    await dp.storage.wait_closed()

def main():
    logging.basicConfig(level=logging.INFO)
    start_webhook(dispatcher=dp, webhook_path=WEBHOOK_PATH, on_startup=on_startup, on_shutdown=on_shutdown,
                  skip_updates=True, host=WEBAPP_HOST, port=WEBAPP_PORT)

if __name__ == '__main__':
    main()