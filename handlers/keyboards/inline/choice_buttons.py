from typing import ItemsView, Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, inline_keyboard
from .callback_data import currency, convert_currency_data

choice = InlineKeyboardMarkup(
    inline_keyboard = [
        [
            InlineKeyboardButton(text="\U0001F1FA\U0001F1F8 Доллар", callback_data=currency.new(
                item_id=1
            )),
            InlineKeyboardButton(text="\U0001F1FA\U0001F1FF Cум", callback_data=currency.new(
                item_id=2
            )),
        ], [
            InlineKeyboardButton(text="\U0001F1F0\U0001F1EC Cом", callback_data=currency.new(
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
            KeyboardButton(text="➕ Прибыль"),
            KeyboardButton(text="➖ Затрата")
        ],
        [
            KeyboardButton(text="❌ Отмена")
        ]
    ],
    resize_keyboard=True
)

convert_currency = InlineKeyboardMarkup(
    inline_keyboard = [
        [
            InlineKeyboardButton(text="\U0001F1FA\U0001F1F8 Доллар", callback_data=convert_currency_data.new(
                exchange_rate="USD"
            )),
            InlineKeyboardButton(text="\U0001F1FA\U0001F1FF Cум", callback_data=convert_currency_data.new(
                exchange_rate="UZS"
            )),
            InlineKeyboardButton(text="\U0001F1F0\U0001F1EC Cом", callback_data=convert_currency_data.new(
                exchange_rate="KGS"
            ))
        ], [
            InlineKeyboardButton(text="❌ Отмена", callback_data=convert_currency_data.new(
                exchange_rate="None"
            ))
        ]
    ]
)

prompt_cancel_button = InlineKeyboardMarkup(
    inline_keyboard = [
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data=currency.new(
                item_id=4
            ))
        ]
    ]
)