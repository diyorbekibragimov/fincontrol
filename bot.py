import logging
from aiogram import (Bot, Dispatcher, executor)
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContextProxy
from filters import (IsOwnerFilter, IsAdminFilter, MemberCanRestrictFilter)
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from handlers.keyboards.inline.choice_buttons import (choice, confirm, operation, convert_currency, prompt_cancel_button)
from handlers.keyboards.inline.callback_data import (currency, convert_currency_data)
from config import (BOT_TOKEN, WEBHOOK_URL, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_PATH)
from functions import (converter as conv, sep)
from config import URL
from db import BotDB

# init
BotDB = BotDB()

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
    change = State()
    quantity = State()
    to_currency = State()
    lastchange = State()

class CurrencyChange(StatesGroup):
    start = State()
    change = State()

class ChooseCurrency(StatesGroup):
    start = State()

def instructions(currency = None):
    text = ""
    if currency:
        text += f"<i>Ваша основная валюта теперь - <b>{currency}</b></i>\n\n"
    text += "<b>Мои возможности:</b>\n\n" \
            "/record - Записать прибыль/убыток\n" \
            "/currency - Изменить основную валюту\n" \
            "/history - Просмотреть вашу историю\n" \
            "/convert - Конвертация валют\n" \
            "/exrate - Курс доллара"
    return text

@dp.message_handler(state=ChooseCurrency.start)
async def invalidCurrencyId(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if data["start"] == "change":
            await state.finish()
            await CurrencyChange.change.set()
            return await message.answer("Вы хотите отменить операцию?", reply_markup=confirm)
    await message.answer(text="Выберите основную валюту",
                            reply_markup=choice)
# Handling all commands of bot
@dp.message_handler(state='*', commands = "start")
async def start(message: Message, state: FSMContext):
    await state.finish()

    if (not BotDB.user_exists(message.from_user.id)):
        await ChooseCurrency.start.set()
        await message.answer(text="Выберите основную валюту",
                            reply_markup=choice)
    else:
        await message.answer(f"Добро пожаловать, {message.from_user.username}!")
        await message.answer(text=instructions())

@dp.message_handler(state='*', commands="history", commands_prefix="/")
async def history(message: Message, state=FSMContext):
    await state.finish()
    currencyData = BotDB.get_user_currency(user_id=message.from_user.id)
    currency = currencyData[1]
    records = BotDB.get_main_records(message.from_user.id)
    context = dict() # declaring a variable to save all data needed to display
    
    for (key, value) in records.items():
        profit = 0.0
        spending = 0.0
        total = 0.0

        for r in value:
            r = tuple(r)
            if r[0]: # check if operation is profit
                profit += float(r[1])
                total += float(r[1])
            else: # otherwise it is spending
                spending += float(r[1])
                total -= float(r[1])
        res = {
            "profit": "{:,.2f}".format(profit),
            "spending": "{:,.2f}".format(spending),
            "total": "{:,.2f}".format(total)
        }
        context[key] = res
    shortcut = BotDB.get_user_currency(message.from_user.id)
    shortcut = shortcut[2]

    text = f"✅ Основная валюта - <b>{currency}</b>\n\n" \
            "<b>Выписка за день:</b>\n" \
            f"➕ Доход - <b>{context['day']['profit']}</b> <i>{shortcut}</i>\n" \
            f"➖ Расход - <b>{context['day']['spending']}</b> <i>{shortcut}</i>\n" \
            f"💰 Общая сумма: <b>{context['day']['total']}</b> <i>{shortcut}</i>\n\n" \
            "<b>Выписка за Неделю:</b>\n" \
            f"➕ Доход - <b>{context['week']['profit']}</b> <i>{shortcut}</i>\n" \
            f"➖ Расход - <b>{context['week']['spending']}</b> <i>{shortcut}</i>\n" \
            f"💰 Общая сумма: <b>{context['week']['total']}</b> <i>{shortcut}</i>\n\n" \
            "<b>Выписка за Месяцв:</b>\n" \
            f"➕ Доход - <b>{context['month']['profit']}</b> <i>{shortcut}</i>\n" \
            f"➖ Расход - <b>{context['month']['spending']}</b> <i>{shortcut}</i>\n" \
            f"💰 Общая сумма: <b>{context['month']['total']}</b> <i>{shortcut}</i>\n"
            
    await message.answer(text)
    await message.answer(text=instructions())

@dp.message_handler(state='*', commands = ("currency"), commands_prefix="/")
async def handleCurrencyCommand(message: Message, state: FSMContext):
    await state.finish()
    await CurrencyChange.start.set()
    result = BotDB.get_user_currency(user_id=message.from_user.id)
    currency = result[1]
    await message.answer(text=f"Основная валюта - <b>{currency}</b>\n" \
                            "Изменить валюту?", reply_markup=confirm)

@dp.message_handler(Text(equals=["✅ Да", "❌ Нет"]), state=CurrencyChange.start)
async def handleConfirmBtn(message: Message, state: FSMContext):
    if message.text == "✅ Да":
        await ChooseCurrency.start.set()
        async with state.proxy() as data:
            data["start"] = "change"
        await message.answer(text="✅ Отлично!", reply_markup=ReplyKeyboardRemove())
        await message.answer(text="Выберите основную валюту",
                            reply_markup=choice)
    else:
        await state.finish()
        await message.answer(text=instructions(), reply_markup=ReplyKeyboardRemove())

@dp.message_handler(state=CurrencyChange.start)
async def invalidResponse(message: Message, state: FSMContext):
    await state.finish()
    await message.answer(text=instructions(), reply_markup=ReplyKeyboardRemove())

@dp.message_handler(Text(equals=["✅ Да", "❌ Нет"]), state=CurrencyChange.change)
async def handleConfirmCurrencyButton(message: Message, state: FSMContext):
    if message.text == "✅ Да":
        await state.finish()
        await message.answer(text=instructions(), reply_markup=ReplyKeyboardRemove())
    else:
        await ChooseCurrency.start.set()
        async with state.proxy() as data:
            data["start"] = "change"
        await message.answer("✅ Отлично!", reply_markup=ReplyKeyboardRemove())
        await message.answer("Выберите основную валюту", reply_markup=choice)

# Handling queries to choose the main curreny for user
@dp.callback_query_handler(currency.filter(item_id='1'), state=ChooseCurrency.start)
async def process_callback_currency(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=60)
    await state.finish()
    if (not BotDB.user_exists(query.from_user.id)):
        BotDB.add_user(user_id=query.from_user.id, main_currency = callback_data['item_id'])
        await query.message.edit_text(text=instructions())
    else:
        currency = BotDB.get_user_currency(user_id=query.from_user.id)
        prevExrate = currency[3]
        newExrate = "USD"
        BotDB.edit_currency(user_id=query.from_user.id, main_currency=callback_data['item_id'], prev_exrate=prevExrate, new_exrate=newExrate)
        await query.message.edit_text(text=instructions(currency="Американский доллар"))

@dp.callback_query_handler(currency.filter(item_id='2'), state=ChooseCurrency.start)
async def process_callback_currency(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=60)
    await state.finish()
    if (not BotDB.user_exists(query.from_user.id)):
        BotDB.add_user(user_id=query.from_user.id, main_currency = callback_data['item_id'])
        await query.message.edit_text(text=instructions())
    else:
        currency = BotDB.get_user_currency(user_id=query.from_user.id)
        prevExrate = currency[3]
        newExrate = "UZS"
        BotDB.edit_currency(user_id=query.from_user.id, main_currency=callback_data['item_id'], prev_exrate=prevExrate, new_exrate=newExrate)
        await query.message.edit_text(text=instructions(currency="Узбекский сум"))

@dp.callback_query_handler(currency.filter(item_id='3'), state=ChooseCurrency.start)
async def process_callback_currency(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=60)
    await state.finish()
    if (not BotDB.user_exists(query.from_user.id)):
        BotDB.add_user(user_id=query.from_user.id, main_currency = callback_data['item_id'])
        await query.message.edit_text(text=instructions())
    else:
        currency = BotDB.get_user_currency(user_id=query.from_user.id)
        prevExrate = currency[3]
        newExrate = "KGS"
        BotDB.edit_currency(user_id=query.from_user.id, main_currency=callback_data['item_id'], prev_exrate=prevExrate, new_exrate=newExrate)
        await query.message.edit_text(text=instructions(currency="Киргизский сом"))

@dp.message_handler(commands=("record"), commands_prefix="/", state="*")
async def record(message: Message, state: FSMContext):
    await state.finish()
    await Form.operation.set()
    await message.answer("Какую операцию вы хотите выполнить?", reply_markup=operation)

@dp.message_handler(lambda message: message.text not in ["➕ Прибыль", "➖ Затрата", "❌ Отмена"], state=Form.operation)
async def process_record_invalid(message: Message):
    return await message.reply("❌ Выберите одну из трёх кнопок")

@dp.message_handler(state=Form.operation)
async def process_operation(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await message.answer("✅ Операция отменена!", reply_markup=ReplyKeyboardRemove())
        await message.answer(text=instructions())
        return await state.finish()
    async with state.proxy() as data:
        data["operation"] = message.text
    await Form.next()
    await message.answer("✅ Отлично!", reply_markup=ReplyKeyboardRemove())
    await message.answer("Теперь введите сумму", reply_markup=prompt_cancel_button)

@dp.callback_query_handler(currency.filter(item_id=0), state=Form.quantity)
async def handlePromptCancel(query: CallbackQuery, state: FSMContext):
    await state.finish()
    await query.message.edit_text(text=instructions())

@dp.message_handler(regexp=r"\d+(?:.\d+)?", state=Form.quantity)
async def process_quantity(message: Message, state: FSMContext):
    operation = ""
    res = 0.0
    if message.text.count(",") > 0:
        try:
            res += separator.format_number(message.text)
        except ValueError:
            return await message.reply("❌ Невозожно определить сумму")
    else:
        res += round(float(message.text), 2)
    async with state.proxy() as data:
        data["quantity"] = res
        operation = "+" if data["operation"].count("Прибыль") != 0 else "-"
    BotDB.add_record(message.from_user.id, operation, res)
    await message.answer("✅ Сумма успешно записана!")
    await message.answer(text=instructions())
    # Finish the state
    await state.finish()

@dp.message_handler(state=Form.quantity)
async def process_record_invalid(message: Message):
    return await message.reply("❌ Невозожно определить сумму")

@dp.message_handler(state='*', commands=("exrate"), commands_prefix="/")
async def show_exrate(message: Message, state: FSMContext):
    await state.finish()

    data = converter.show_exrate(["UZS", "KGS"])
    uzs = "{:,.2f}".format(data[0])
    kgs = "{:,.2f}".format(data[1])
    text = f"\U0001F1FA\U0001F1F8 1 USD - \U0001F1FA\U0001F1FF {uzs} UZS\n" \
            f"\U0001F1FA\U0001F1F8 1 USD - \U0001F1F0\U0001F1EC {kgs} KGS"
    await message.answer(text)

@dp.message_handler(state='*', commands=("convert"), commands_prefix="/")
async def convert(message: Message, state: FSMContext):
    await state.finish()
    await ConvertForm.from_currency.set()
    await message.answer(text="Из какой валюты перевести?", reply_markup=convert_currency)

@dp.callback_query_handler(convert_currency_data.filter(exchange_rate="None"), state=ConvertForm.from_currency)
async def handleCancelCurrency(query: CallbackQuery, state: FSMContext):
    await state.finish()
    await query.message.edit_text(text=instructions())

@dp.callback_query_handler(convert_currency_data.filter(exchange_rate="USD"), state=ConvertForm.from_currency)
async def process_from_currency(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=60)
    async with state.proxy() as data:
        data["from_currency"] = callback_data['exchange_rate']
    await ConvertForm.quantity.set()
    await query.message.edit_text("Введите сумму", reply_markup=prompt_cancel_button) 

@dp.callback_query_handler(convert_currency_data.filter(exchange_rate="UZS"), state=ConvertForm.from_currency)
async def process_from_currency(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=60)
    async with state.proxy() as data:
        data["from_currency"] = callback_data['exchange_rate']
    await ConvertForm.quantity.set()
    await query.message.edit_text("Введите сумму", reply_markup=prompt_cancel_button) 

@dp.callback_query_handler(convert_currency_data.filter(exchange_rate="KGS"), state=ConvertForm.from_currency)
async def process_from_currency(query: CallbackQuery, callback_data: dict, state: FSMContext):
    await query.answer(cache_time=60)
    async with state.proxy() as data:
        data["from_currency"] = callback_data['exchange_rate']
    await ConvertForm.quantity.set()
    await query.message.edit_text("Введите сумму", reply_markup=prompt_cancel_button)

@dp.message_handler(state=ConvertForm.from_currency)
async def invalidConvertFormResponse(message: Message):
    await ConvertForm.next()
    await message.answer("Вы хотите отменить операцию?", reply_markup=confirm)

@dp.message_handler(Text(equals=["✅ Да", "❌ Нет"]), state=ConvertForm.change)
async def handleConfirmConvertForm(message: Message, state: FSMContext):
    if message.text == "✅ Да":
        await state.finish()
        await message.answer(text=instructions(), reply_markup=ReplyKeyboardRemove())
    else:
        await ConvertForm.previous()
        await message.answer("✅ Отлично!", reply_markup=ReplyKeyboardRemove())
        await message.answer(text="Из какой валюты?", reply_markup=convert_currency)

@dp.message_handler(state=ConvertForm.change)
async def invalidConfirmFormResponse(message: Message):
    await message.answer("Вы хотите отменить операцию?")

@dp.callback_query_handler(currency.filter(item_id=0), state=ConvertForm.quantity)
async def handleCancelQuantity(querry: CallbackQuery, state: FSMContext):
    await state.finish()
    await querry.message.edit_text(text=instructions())

@dp.message_handler(regexp=r"\d+(?:.\d+)?", state=ConvertForm.quantity)
async def process_quantity(message: Message, state: FSMContext):
    amount = 0.0
    if message.text.count(",") > 0:
        try:
            amount += separator.format_number(message.text)
        except ValueError:
            return await message.reply("❌ Невозожно определить сумму")
    else:
        amount += round(float(message.text), 2)
    
    async with state.proxy() as data:
        data["quantity"] = amount
    await ConvertForm.next()
    await message.answer("В какую валюту перевести?",  reply_markup=convert_currency)

@dp.message_handler(state=ConvertForm.quantity)
async def process_invalid_quantity(message: Message):
    return await message.reply("❌ Невозожно определить сумму")

@dp.callback_query_handler(convert_currency_data.filter(exchange_rate="None"), state=ConvertForm.to_currency)
async def handleCancelCurrency(query: CallbackQuery, state: FSMContext):
    await state.finish()
    await query.message.edit_text(text=instructions())

@dp.callback_query_handler(convert_currency_data.filter(exchange_rate="USD"), state=ConvertForm.to_currency)
async def process_to_currency(query: CallbackQuery, callback_data: dict, state: FSMContext):
    amount = 0.0
    text = ""
    async with state.proxy() as data:
        data["to_currency"] = callback_data["exchange_rate"]
        amount += converter.convert(data["from_currency"], data["to_currency"], data["quantity"])
        from_quantity = "{:,.2f}".format(data["quantity"])
        amount = "{:,.2f}".format(amount)
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
        from_quantity = "{:,.2f}".format(data["quantity"])
        amount = "{:,.2f}".format(amount)
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
        from_quantity = "{:,.2f}".format(data["quantity"])
        amount = "{:,.2f}".format(amount)
        text += "<b>Результат:</b>\n" \
                f"<b>{from_quantity}</b> {data['from_currency']} = <b>{amount}</b> {data['to_currency']}"
    await query.message.edit_text(text=text)
    await state.finish()

@dp.message_handler(state=ConvertForm.to_currency)
async def invalidConvertFormToCurrencyResponse(message: Message):
    await ConvertForm.next()
    await message.answer("Вы хотите отменить операцию?", reply_markup=confirm)

@dp.message_handler(Text(equals=["✅ Да", "❌ Нет"]), state=ConvertForm.lastchange)
async def handleConfirmConvertForm(message: Message, state: FSMContext):
    if message.text == "✅ Да":
        await state.finish()
        await message.answer(text=instructions(), reply_markup=ReplyKeyboardRemove())
    else:
        await ConvertForm.previous()
        await message.answer("✅ Отлично!", reply_markup=ReplyKeyboardRemove())
        await message.answer(text="В какую валюту?", reply_markup=convert_currency)

@dp.message_handler(state=ConvertForm.lastchange)
async def invalidConfirmConvertFormResponse(message: Message):
    await message.answer("Вы хотите отменить операцию?")

@dp.message_handler(state="*")
async def handleAnyCase(message: Message):
    await message.answer(text=instructions())

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