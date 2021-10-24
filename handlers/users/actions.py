from logging import BASIC_FORMAT
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from aiogram.dispatcher.filters.state import State, StatesGroup
from dispatcher import dp
from aiogram.dispatcher.filters import Text
import re
from bot import BotDB

from handlers.keyboards.inline.choice_buttons import choice, confirm, operation
from handlers.keyboards.inline.callback_data import currency


class Form(StatesGroup):
    operation = State()
    quantity = State()

def instructions():
    text = "<b>Мои возможности:</b>\n" \
            "/record - Записать убыток или прибыль за день\n" \
            "/history - Просмотреть затраты и доходы\n" \
            "/currency - Изменить основную валюту\n" \
            "/profile - Просмотреть ваш профиль"
    return text

# Handling queries to choose the main curreny for user
@dp.callback_query_handler(currency.filter(item_id='1'))
async def process_callback_currency(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=60)
    if (not BotDB.user_exists(query.from_user.id)):
        BotDB.add_user(user_id=query.from_user.id, main_currency = callback_data['item_id'])
    else:
        currency = BotDB.get_user_currency(user_id=query.from_user.id)
        prevExrate = currency[3]
        newExrate = "USD"
        BotDB.edit_currency(user_id=query.from_user.id, main_currency=callback_data['item_id'], prev_exrate=prevExrate, new_exrate=newExrate)
    await query.message.edit_text(text=instructions())

@dp.callback_query_handler(currency.filter(item_id='2'))
async def process_callback_currency(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=60)
    if (not BotDB.user_exists(query.from_user.id)):
        BotDB.add_user(user_id=query.from_user.id, main_currency = callback_data['item_id'])
    else:
        currency = BotDB.get_user_currency(user_id=query.from_user.id)
        prevExrate = currency[3]
        newExrate = "UZS"
        BotDB.edit_currency(user_id=query.from_user.id, main_currency=callback_data['item_id'], prev_exrate=prevExrate, new_exrate=newExrate)

    await query.message.edit_text(text=instructions())

@dp.callback_query_handler(currency.filter(item_id='3'))
async def process_callback_currency(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=60)
    if (not BotDB.user_exists(query.from_user.id)):
        BotDB.add_user(user_id=query.from_user.id, main_currency = callback_data['item_id'])
    else:
        currency = BotDB.get_user_currency(user_id=query.from_user.id)
        prevExrate = currency[3]
        newExrate = "KGS"
        BotDB.edit_currency(user_id=query.from_user.id, main_currency=callback_data['item_id'], prev_exrate=prevExrate, new_exrate=newExrate)
    await query.message.edit_text(text=instructions())

# Handling all commands of bot
@dp.message_handler(commands = "start")
async def start(message: Message):
    if (not BotDB.user_exists(message.from_user.id)):
        await message.answer(text="Выберите основную валюту",
                            reply_markup=choice)
    else:
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
    await message.answer(text=f"Ваша основная валюта - <b>{currency}</b>\n" \
                            "Изменить валюту?", reply_markup=confirm)

@dp.message_handler(Text(equals=["✅ Да", "❌ Нет"]))
async def handleConfirmBtn(message: Message):
    if message.text == "✅ Да":
        message.reply_markup = ReplyKeyboardRemove()
        await message.answer(text="Хорошо!", reply_markup=ReplyKeyboardRemove())
        await message.answer(text="Выберите основную валюту:",
                            reply_markup=choice)
    elif message.text == "❌ Нет":
        await message.answer(text=instructions(), reply_markup=ReplyKeyboardRemove())

@dp.message_handler(commands=("record"), commands_prefix="/")
async def record(message: Message):
    await Form.operation.set()
    await message.answer("Какую операцию вы хотите выполнить:", reply_markup=operation)

@dp.message_handler(lambda message: message.text not in ["Прибыль", "Убыток"], state=Form.operation)
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
    async with state.proxy() as data:
        data["quantity"] = float(message.text.replace(",", ""))
        operation = "+" if data["operation"] == "Прибыль" else "-"
    BotDB.add_record(message.from_user.id, operation, float(message.text))
    await message.answer("✅ Сумма успешно записано!")
    # Finish the state
    await state.finish()

@dp.message_handler(state=Form.quantity)
async def process_record_invalid(message: Message):
    return await message.reply("❌ Невозожно определить сумму.")

# @dp.message_handler(commands = ("history", "h"), commands_prefix = "/!")
# async def history(message: Message):
#     # Handling the command of watching all transactions in a day/week/month/year
#     cmd_variants = ("/history", "/h", "!history", "!h")
#     within_als = {
#         "day": ("today", "day", "сегодня", "день"),
#         "week": ("week", "неделя", "неделю"),
#         "month": ("month", "месяц"),
#         "year": ("year", "год")
#     }

#     cmd = message.text
#     for r in cmd_variants:
#         cmd = cmd.replace(r, '').strip()
    
#     within = "day" # default
#     if(len(cmd)):
#         for k in within_als:
#             for als in within_als[k]:
#                 if (als == cmd):
#                     within = k

#     #fetch
#     records = BotDB.get_records(message.from_user.id, within)

#     if(len(records)):
#         answer = f"⏳ История операций за {within_als[within][-1]}\n\n"

#         for r in records:
#             answer += "<b>" + ("➖ Расход" if not r[2] else "➕ Доход") + "</b>"
#             answer += f' - {r[3]}'
#             answer += f' <i>({r[4]})</i>\n'

#         await message.answer(answer)
#     else: 
#         await message.answer("❌ Записей не обнаружено!")