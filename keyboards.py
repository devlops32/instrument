from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import inline_keyboard

def main_reply_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📥 Парсить"), KeyboardButton(text="📤 Инвайтить")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def main_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📥 Парсить", callback_data="parse"),
                InlineKeyboardButton(text="📤 Инвайтить", callback_data="invite")
            ],
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
                InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")
            ]
        ]
    )

def after_parse_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Пригласить всех", callback_data="invite_all")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ]
    )