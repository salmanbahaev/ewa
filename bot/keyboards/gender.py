"""Gender selection keyboard"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_gender_keyboard() -> InlineKeyboardMarkup:
    """
    Get gender selection keyboard.
    
    Returns:
        InlineKeyboardMarkup with male/female buttons
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="👨 Мужчина",
                callback_data="gender_male"
            ),
            InlineKeyboardButton(
                text="👩 Девушка",
                callback_data="gender_female"
            )
        ]
    ])
    return keyboard

