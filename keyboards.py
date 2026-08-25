from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_reply_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📥 Парсить"), KeyboardButton(text="📤 Инвайтить")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="ℹ️ Помощь")],
            [KeyboardButton(text="🔑 Авторизация")]
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
            ],
            [
                InlineKeyboardButton(text="🔑 Авторизация", callback_data="auth")
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

def cancel_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_auth")]
        ]
    )

def retry_auth_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Запросить новый код", callback_data="retry_auth")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_auth")]
        ]
    )