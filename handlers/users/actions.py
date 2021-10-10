from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types.reply_keyboard import ReplyKeyboardRemove
from dispatcher import dp
from aiogram.dispatcher.filters import Text
import re
from bot import BotDB

from handlers.keyboards.inline.choice_buttons import choice, confirm
from handlers.keyboards.inline.callback_data import currency


# addRecordCon = False

def instructions(main_currency = None, user_id = -1):
    if main_currency == None and user_id != -1:
        main_currency = BotDB.get_user_currency(user_id=user_id)
    text = f"Основная валюта - <b>{main_currency}</b>\n\n" \
            "<b>Мои возможности:</b>\n" \
            "/exp - <i>Записать убыток за день</i>\n" \
            "/profit - <i>Записать прибыль за день</i>\n" \
            "/history - <i>Просмотреть затраты и доходы</i>\n" \
            "/currency - <i>Изменить основную валюту</i>"
    return text

# Handling queries to choose the main curreny for user
@dp.callback_query_handler(currency.filter(item_id='1'))
async def process_callback_currency(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=60)
    if (not BotDB.user_exists(query.from_user.id)):
        BotDB.add_user(user_id=query.from_user.id, main_currency = callback_data['item_id'])
    else:
        BotDB.edit_currency(user_id=query.from_user.id, main_currency=callback_data['item_id'])
    await query.message.edit_text(text=instructions(main_currency = "Американский доллар"))

@dp.callback_query_handler(currency.filter(item_id='2'))
async def process_callback_currency(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=60)
    if (not BotDB.user_exists(query.from_user.id)):
        BotDB.add_user(user_id=query.from_user.id, main_currency = callback_data['item_id'])
    else:
        BotDB.edit_currency(user_id=query.from_user.id, main_currency=callback_data['item_id'])
    await query.message.edit_text(text=instructions(main_currency = "Узбекский сум"))

@dp.callback_query_handler(currency.filter(item_id='3'))
async def process_callback_currency(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=60)
    if (not BotDB.user_exists(query.from_user.id)):
        BotDB.add_user(user_id=query.from_user.id, main_currency = callback_data['item_id'])
    else:
        BotDB.edit_currency(user_id=query.from_user.id, main_currency=callback_data['item_id'])
    await query.message.edit_text(text=instructions(main_currency = "Киргизский сом"))

# Handling all commands of bot
@dp.message_handler(commands = "start")
async def start(message: Message):
    if (not BotDB.user_exists(message.from_user.id)):
        await message.answer(text="Выберите основную валюту",
                            reply_markup=choice)
    else:
        await message.answer(text=instructions(user_id=message.from_user.id))

@dp.message_handler(commands = ("currency"), commands_prefix="/")
async def currency(message: Message):
    result = BotDB.get_user_currency(user_id=message.from_user.id)
    await message.answer(text=f"Ваша основная валюта - <b>{result}</b>\n" \
                            "Изменить валюту?", reply_markup=confirm)

@dp.message_handler(Text(equals=["✅ Да", "❌ Нет"]))
async def handleConfirmBtn(message: Message):
    if message.text == "✅ Да":
        message.reply_markup = ReplyKeyboardRemove()
        await message.answer(text="Хорошо!", reply_markup=ReplyKeyboardRemove())
        await message.answer(text="Выберите основную валюту:",
                            reply_markup=choice)
    elif message.text == "❌ Нет":
        await message.answer(text=instructions(user_id=message.from_user.id), reply_markup=ReplyKeyboardRemove())

@dp.message_handler(commands = ("exp", "profit"), commands_prefix = "/")
async def record(message: Message):
    cmd_variants = (("/exp"), ("/profit"))
    operation = '-' if message.text.startswith(cmd_variants[0]) else '+'

# @dp.message_handler(regexp="\d+(?:.\d+)?")
# async def addRecord(message: Message):

        # addRecordCon = False
# def addRecord(operation):

# def addRecord(value):
#     if (len(value)):
# regexp="\d+(?:.\d+)?"
#         x = re.findall(r"", value)

#         if (len(x)):
#             value = float(x[0].replace(',', '.'))

#             BotDB.add_record(message.from_user.id, operation, value)

#             if (operation == '-'):
#                 await message.reply("✅ Запись о <u><b>расходе</b></u> успешно внесена!")
#             else:
#                 await message.reply("✅ Запись о <u><b>доходе</b></u> успешно внесена!")
#         else:
#             await message.reply("❌ Не удалось определить сумму!")
#     else:
#         await message.reply("❌ Не введена сумма!")


@dp.message_handler(commands = ("history", "h"), commands_prefix = "/!")
async def history(message: Message):
    # Handling the command of watching all transactions in a day/week/month/year
    cmd_variants = ("/history", "/h", "!history", "!h")
    within_als = {
        "day": ("today", "day", "сегодня", "день"),
        "week": ("week", "неделя", "неделю"),
        "month": ("month", "месяц"),
        "year": ("year", "год")
    }

    cmd = message.text
    for r in cmd_variants:
        cmd = cmd.replace(r, '').strip()
    
    within = "day" # default
    if(len(cmd)):
        for k in within_als:
            for als in within_als[k]:
                if (als == cmd):
                    within = k

    #fetch
    records = BotDB.get_records(message.from_user.id, within)

    if(len(records)):
        answer = f"⏳ История операций за {within_als[within][-1]}\n\n"

        for r in records:
            answer += "<b>" + ("➖ Расход" if not r[2] else "➕ Доход") + "</b>"
            answer += f' - {r[3]}'
            answer += f' <i>({r[4]})</i>\n'

        await message.answer(answer)
    else: 
        await message.answer("❌ Записей не обнаружено!")