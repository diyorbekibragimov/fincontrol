from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .callback_data import currency

choice = InlineKeyboardMarkup(
    inline_keyboard = [
        [
            InlineKeyboardButton(text=":us: Доллар", callback_data=currency.new(
                item_id=1
            )),
            InlineKeyboardButton(text=":flag-uz: Узбекский сум", callback_data=currency.new(
                item_id=2
            )),
        ], [
            InlineKeyboardButton(text=":flag-kg: Киргизский сом", callback_data=currency.new(
                item_id=3
            )),
        ]
    ]
)