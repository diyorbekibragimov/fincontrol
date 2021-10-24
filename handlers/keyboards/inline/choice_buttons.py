from typing import ItemsView, Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, inline_keyboard
from .callback_data import currency

choice = InlineKeyboardMarkup(
    inline_keyboard = [
        [
            InlineKeyboardButton(text="\U0001F1FA\U0001F1F8 Доллар", callback_data=currency.new(
                item_id=1
            )),
            InlineKeyboardButton(text="\U0001F1FA\U0001F1FF Узбекский сум", callback_data=currency.new(
                item_id=2
            )),
        ], [
            InlineKeyboardButton(text="\U0001F1F0\U0001F1EC Киргизский сом", callback_data=currency.new(
                item_id=3
            )),
        ]
    ]
)

confirm = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton("✅ Да"),
            KeyboardButton("❌ Нет"),
        ]
    ],
    resize_keyboard = True
)

operation = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text="Прибыль"),
            KeyboardButton(text="Убыток")
        ]
    ],
    resize_keyboard=True
)