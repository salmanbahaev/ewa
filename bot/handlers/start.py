"""Start command handler"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from data.database import Database
from bot.keyboards.gender import get_gender_keyboard
from bot.keyboards.reply import get_main_menu_keyboard
import config

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, db: Database):
    """
    Handle /start command.
    
    Args:
        message: Telegram message
        db: Database instance
    """
    user = message.from_user
    logger.info(f"User {user.id} (@{user.username}) started the bot")
    
    # Add user to database
    await db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    
    # Check if user has already selected assistant gender
    gender = await db.get_assistant_gender(user.id)
    
    if gender:
        # User already selected gender - show personalized welcome
        # Try to transliterate name if it looks like a name
        first_name = user.first_name
        name_map = {
            "Salman": "Салман",
            "Muhammad": "Мухаммад", 
            "Ahmed": "Ахмед",
            "Ali": "Али",
            "Omar": "Омар"
        }
        display_name = name_map.get(first_name, first_name)
        
        if gender == "male":
            welcome_text = f"""Здравствуйте, {display_name}! Сергей на связи.

🛍 **EWA PRODUCT** - премиальные БАДы, нутрицевтики и косметика для здоровья и красоты.

💡 **Что я могу:**
• Подобрать продукты под вашу задачу
• Рассказать о составе и применении
• Найти товары по категориям
• Ответить на вопросы о компании

**Примеры вопросов:**
"Что для суставов?" • "Покажи для похудения"
"Что для мозга и памяти?" • "Нужен коллаген"

Чем могу быть полезен?"""
        else:
            welcome_text = f"""Здравствуйте, {display_name}! Екатерина на связи 😊

🛍 **EWA PRODUCT** - премиальные БАДы, нутрицевтики и косметика для здоровья и красоты.

💡 **Что я могу:**
• Подобрать продукты под вашу задачу
• Рассказать о составе и применении
• Найти товары по категориям
• Ответить на вопросы о компании

**Примеры вопросов:**
"Что для суставов?" • "Покажи для похудения"
"Что для кожи лица?" • "Нужен коллаген"

Чем могу помочь?"""
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu_keyboard()
        )
    else:
        # First time user - ask to select assistant gender
        welcome_text = f"""👋 Здравствуйте, {user.first_name}!

Добро пожаловать в **EWA PRODUCT** - магазин премиальных БАДов, нутрицевтиков и косметики.

🎯 **Что у нас есть:**
• БАДы для здоровья (мозг, иммунитет, суставы, печень)
• Продукты для похудения и детокса
• Коллаген и anti-age решения
• Косметика для лица, тела и волос
• Функциональное питание

💬 **Я помогу:**
Подобрать продукты под вашу задачу, рассказать о составе, ответить на вопросы о компании.

**Выберите, с кем Вам удобнее общаться:**"""
        
        await message.answer(welcome_text, reply_markup=get_gender_keyboard())

