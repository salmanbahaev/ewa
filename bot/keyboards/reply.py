"""Reply keyboard for main menu"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Get main menu reply keyboard (always visible).
    
    Returns:
        ReplyKeyboardMarkup with menu buttons
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔄 Сменить ассистента"),
                KeyboardButton(text="🗑 Очистить историю")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

