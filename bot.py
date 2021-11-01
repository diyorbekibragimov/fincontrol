import logging
from aiogram import (Bot, Dispatcher, executor)
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from filters import (IsOwnerFilter, IsAdminFilter, MemberCanRestrictFilter)
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from handlers.keyboards.inline.choice_buttons import (choice, confirm, operation, convert_currency)
from handlers.keyboards.inline.callback_data import (currency, convert_currency_data)
from config import (BOT_TOKEN, WEBHOOK_URL, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_PATH)
from functions import (converter as conv, sep)
from config import URL
from db import BotDB

# init
BotDB = BotDB('fincontrol.db')

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

# activate filters
dp.filters_factory.bind(IsOwnerFilter)
dp.filters_factory.bind(IsAdminFilter)
dp.filters_factory.bind(MemberCanRestrictFilter)


converter = conv.RealTimeCurrencyConverter(URL)
separator = sep.Separator()

class Form(StatesGroup):
    operation = State()
    quantity = State()

class ConvertForm(StatesGroup):
    from_currency = State()
    quantity = State()
    to_currency = State()

def instructions(currency = None):
    text = ""
    if currency:
        text += f"<i>Ваша основная валюта теперь - <b>{currency}</b></i>\n\n"
    text += "<b>Мои возможности:</b>\n\n" \
            "/record - Записать прибыль/убыток\n" \
            "/currency - Изменить основную валюту\n" \
            "/profile - Просмотреть ваш профиль\n" \
            "/convert - Конвертация валют\n" \
            "/exrate - Курс доллара"
    return text

# Handling queries to choose the main curreny for user
@dp.callback_query_handler(currency.filter(item_id='1'))
async def process_callback_currency(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=60)
    if (not BotDB.user_exists(query.from_user.id)):
        BotDB.add_user(user_id=query.from_user.id, main_currency = callback_data['item_id'])
        await query.message.edit_text(text=instructions())
    else:
        currency = BotDB.get_user_currency(user_id=query.from_user.id)
        prevExrate = currency[3]
        newExrate = "USD"
        BotDB.edit_currency(user_id=query.from_user.id, main_currency=callback_data['item_id'], prev_exrate=prevExrate, new_exrate=newExrate)
        await query.message.edit_text(text=instructions(currency="Американский доллар"))

@dp.callback_query_handler(currency.filter(item_id='2'))
async def process_callback_currency(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=60)
    if (not BotDB.user_exists(query.from_user.id)):
        BotDB.add_user(user_id=query.from_user.id, main_currency = callback_data['item_id'])
        await query.message.edit_text(text=instructions())
    else:
        currency = BotDB.get_user_currency(user_id=query.from_user.id)
        prevExrate = currency[3]
        newExrate = "UZS"
        BotDB.edit_currency(user_id=query.from_user.id, main_currency=callback_data['item_id'], prev_exrate=prevExrate, new_exrate=newExrate)
        await query.message.edit_text(text=instructions(currency="Узбекский сум"))

@dp.callback_query_handler(currency.filter(item_id='3'))
async def process_callback_currency(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=60)
    if (not BotDB.user_exists(query.from_user.id)):
        BotDB.add_user(user_id=query.from_user.id, main_currency = callback_data['item_id'])
        await query.message.edit_text(text=instructions())
    else:
        currency = BotDB.get_user_currency(user_id=query.from_user.id)
        prevExrate = currency[3]
        newExrate = "KGS"
        BotDB.edit_currency(user_id=query.from_user.id, main_currency=callback_data['item_id'], prev_exrate=prevExrate, new_exrate=newExrate)
        await query.message.edit_text(text=instructions(currency="Киргизский сом"))

# Handling all commands of bot
@dp.message_handler(commands = "start")
async def start(message: Message):
    if (not BotDB.user_exists(message.from_user.id)):
        await message.answer(text="Выберите основную валюту",
                            reply_markup=choice)
    else:
        await message.answer(f"Добро пожаловать, {message.from_user.username}!")
        await message.answer(text=instructions())

@dp.message_handler(commands="profile", commands_prefix="/")
async def profile(message: Message):
    currencyData = BotDB.get_user_currency(user_id=message.from_user.id)
    currency = currencyData[1]
    records = BotDB.get_main_records(message.from_user.id)
    context = dict() # declaring a variable to save all data needed to display
    
    for (key, value) in records.items():
        res = {
            "profit": 0.0,
            "spending": 0.0,
            "total": 0.0
        }
        for r in value:
            r = tuple(r)
            if r[0] == 1: # check if operation is profit
                res["profit"] += float(r[1])
                res["total"] += float(r[1])
            else: # otherwise it is spending
                res["spending"] += float(r[1])
                res["total"] -= float(r[1])
        res["profit"] = separator.format_repr(str(res["profit"]))
        res["spending"] = separator.format_repr(str(res["spending"]))
        res["total"] = separator.format_repr(str(res["total"]))
        context[key] = res
    shortcut = BotDB.get_user_currency(message.from_user.id)
    shortcut = shortcut[2]

    text = f"✅ Основная валюта - <b>{currency}</b>\n\n" \
            "<b>За день:</b>\n" \
            f"➕ Доход - <b>{context['day']['profit']}</b> <i>{shortcut}</i>\n" \
            f"➖ Расход - <b>{context['day']['spending']}</b> <i>{shortcut}</i>\n" \
            f"💰 Общая сумма: <b>{context['day']['total']}</b> <i>{shortcut}</i>\n\n" \
            "<b>За неделю:</b>\n" \
            f"➕ Доход - <b>{context['week']['profit']}</b> <i>{shortcut}</i>\n" \
            f"➖ Расход - <b>{context['week']['spending']}</b> <i>{shortcut}</i>\n" \
            f"💰 Общая сумма: <b>{context['week']['total']}</b> <i>{shortcut}</i>\n\n" \
            "<b>За месяц:</b>\n" \
            f"➕ Доход - <b>{context['month']['profit']}</b> <i>{shortcut}</i>\n" \
            f"➖ Расход - <b>{context['month']['spending']}</b> <i>{shortcut}</i>\n" \
            f"💰 Общая сумма: <b>{context['month']['total']}</b> <i>{shortcut}</i>\n"
            
    await message.answer(text)

@dp.message_handler(commands = ("currency"), commands_prefix="/")
async def currency(message: Message):
    result = BotDB.get_user_currency(user_id=message.from_user.id)
    currency = result[1]
    await message.answer(text=f"Основная валюта - <b>{currency}</b>\n" \
                            "Изменить валюту?", reply_markup=confirm)

@dp.message_handler(Text(equals=["✅ Да", "❌ Нет"]))
async def handleConfirmBtn(message: Message):
    if message.text == "✅ Да":
        await message.answer(text="Хорошо", reply_markup=ReplyKeyboardRemove())
        await message.answer(text="Выберите основную валюту:",
                            reply_markup=choice)
    elif message.text == "❌ Нет":
        await message.answer(text=instructions(), reply_markup=ReplyKeyboardRemove())

@dp.message_handler(commands=("record"), commands_prefix="/")
async def record(message: Message):
    await Form.operation.set()
    await message.answer("Какую операцию вы хотите выполнить:", reply_markup=operation)

@dp.message_handler(lambda message: message.text not in ["Прибыль", "Затрата"], state=Form.operation)
async def process_record_invalid(message: Message):
    return await message.reply("Выберите одну из двух кнопок.")

@dp.message_handler(state=Form.operation)
async def process_operation(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["operation"] = message.text
    await Form.next()
    await message.reply("Введите сумму: ",  reply_markup=ReplyKeyboardRemove())

@dp.message_handler(regexp=r"\d+(?:.\d+)?", state=Form.quantity)
async def process_quantity(message: Message, state: FSMContext):
    operation = ""
    res = 0.0
    if message.text.count(",") > 0:
        try:
            res += separator.format_number(message.text)
        except ValueError:
            return await message.reply("❌ Невозожно определить сумму.")
    else:
        res += round(float(message.text), 4)
    async with state.proxy() as data:
        data["quantity"] = res
        operation = "+" if data["operation"] == "Прибыль" else "-"
    BotDB.add_record(message.from_user.id, operation, res)
    await message.answer("✅ Сумма успешно записано!")
    # Finish the state
    await state.finish()

@dp.message_handler(state=Form.quantity)
async def process_record_invalid(message: Message):
    return await message.reply("❌ Невозожно определить сумму.")

@dp.message_handler(commands=("exrate"), commands_prefix="/")
async def show_exrate(message: Message):
    data = converter.show_exrate(["UZS", "KGS"])
    uzs = separator.format_repr(str(data[0]))
    kgs = separator.format_repr(str(data[1]))
    text = f"\U0001F1FA\U0001F1F8 1 USD - \U0001F1FA\U0001F1FF {uzs} UZS\n" \
            f"\U0001F1FA\U0001F1F8 1 USD - \U0001F1F0\U0001F1EC {kgs} KGS"
    await message.answer(text)

@dp.message_handler(commands=("convert"), commands_prefix="/")
async def convert(message: Message):
    await ConvertForm.from_currency.set()
    await message.answer(text="Из какой валюты?", reply_markup=convert_currency)

@dp.callback_query_handler(convert_currency_data.filter(exchange_rate="USD"), state=ConvertForm.from_currency)
async def process_from_currency(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=60)
    async with state.proxy() as data:
        data["from_currency"] = callback_data['exchange_rate']
    await ConvertForm.next()
    await query.message.edit_text("Введите сумму: ") 

@dp.callback_query_handler(convert_currency_data.filter(exchange_rate="UZS"), state=ConvertForm.from_currency)
async def process_from_currency(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=60)
    async with state.proxy() as data:
        data["from_currency"] = callback_data['exchange_rate']
    await ConvertForm.next()
    await query.message.edit_text("Введите сумму: ") 

@dp.callback_query_handler(convert_currency_data.filter(exchange_rate="KGS"), state=ConvertForm.from_currency)
async def process_from_currency(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=60)
    async with state.proxy() as data:
        data["from_currency"] = callback_data['exchange_rate']
    await ConvertForm.next()
    await query.message.edit_text("Введите сумму: ") 

@dp.message_handler(regexp=r"\d+(?:.\d+)?", state=ConvertForm.quantity)
async def process_quantity(message: Message, state: FSMContext):
    amount = 0.0
    if message.text.count(",") > 0:
        try:
            amount += separator.format_number(message.text)
        except ValueError:
            return await message.reply("❌ Невозожно определить сумму.")
    else:
        amount += round(float(message.text), 4)
    
    async with state.proxy() as data:
        data["quantity"] = amount
    await ConvertForm.next()
    await message.reply("В какую валюту?",  reply_markup=convert_currency)

@dp.message_handler(state=ConvertForm.quantity)
async def process_invalid_quantity(message: Message):
    return await message.reply("❌ Невозожно определить сумму.")

@dp.callback_query_handler(convert_currency_data.filter(exchange_rate="USD"), state=ConvertForm.to_currency)
async def process_to_currency(query: CallbackQuery, callback_data: dict, state: FSMContext):
    amount = 0.0
    text = ""
    async with state.proxy() as data:
        data["to_currency"] = callback_data["exchange_rate"]
        amount += converter.convert(data["from_currency"], data["to_currency"], data["quantity"])
        from_quantity = separator.format_repr(str(data["quantity"]))
        amount = separator.format_repr(str(amount))
        text += "<b>Результат:</b>\n" \
                f"<b>{from_quantity}</b> {data['from_currency']} = <b>{amount}</b> {data['to_currency']}"
    await query.message.edit_text(text=text)
    await state.finish()

@dp.callback_query_handler(convert_currency_data.filter(exchange_rate="UZS"), state=ConvertForm.to_currency)
async def process_to_currency(query: CallbackQuery, callback_data: dict, state: FSMContext):
    amount = 0.0
    text = ""
    async with state.proxy() as data:
        data["to_currency"] = callback_data["exchange_rate"]
        amount += converter.convert(data["from_currency"], data["to_currency"], data["quantity"])
        from_quantity = separator.format_repr(str(data["quantity"]))
        amount = separator.format_repr(str(amount))
        text += "<b>Результат:</b>\n" \
                f"<b>{from_quantity}</b> {data['from_currency']} = <b>{amount}</b> {data['to_currency']}"
    await query.message.edit_text(text=text)
    await state.finish()

@dp.callback_query_handler(convert_currency_data.filter(exchange_rate="KGS"), state=ConvertForm.to_currency)
async def process_to_currency(query: CallbackQuery, callback_data: dict, state: FSMContext):
    amount = 0.0
    text = ""
    async with state.proxy() as data:
        data["to_currency"] = callback_data["exchange_rate"]
        amount += converter.convert(data["from_currency"], data["to_currency"], data["quantity"])
        from_quantity = separator.format_repr(str(data["quantity"]))
        amount = separator.format_repr(str(amount))
        text += "<b>Результат:</b>\n" \
                f"<b>{from_quantity}</b> {data['from_currency']} = <b>{amount}</b> {data['to_currency']}"
    await query.message.edit_text(text=text)
    await state.finish()

async def on_startup(dp):
    logging.warning(
        'Starting connection...')
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    logging.warning('Goodbye! Shutting down webhook connection')
    await bot.delete_webhook()

    # Close Redis connection.
    await dp.storage.close()
    await dp.storage.wait_closed()

def main():
    logging.basicConfig(level=logging.INFO)
    executor.start_webhook(dispatcher=dp, webhook_path=WEBHOOK_PATH, on_startup=on_startup, on_shutdown=on_shutdown,
                  skip_updates=True, host=WEBAPP_HOST, port=WEBAPP_PORT)

if __name__ == '__main__':
    main()