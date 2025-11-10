"""Message handlers"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ChatAction
from loguru import logger

from data.database import Database
from ai.assistant import AIAssistant
from bot.keyboards.main import get_main_keyboard
from bot.keyboards.product import get_products_list_keyboard
import config

router = Router()


@router.message(F.text)
async def handle_text_message(message: Message, db: Database, assistant: AIAssistant):
    """
    Handle text messages from users.
    
    Args:
        message: Telegram message
        db: Database instance
        assistant: AI assistant instance
    """
    user = message.from_user
    user_text = message.text
    
    logger.info(f"Message from {user.id} (@{user.username}): {user_text[:100]}")
    
    # Send typing action
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING
    )
    
    try:
        # Ensure user exists in database
        await db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        
        # Add user message to database
        await db.add_message(
            user_id=user.id,
            role="user",
            content=user_text
        )
        
        # Get user's assistant gender preference
        assistant_gender = await db.get_assistant_gender(user.id)
        
        # Get chat history
        history = await db.get_history(
            user_id=user.id,
            limit=config.MAX_HISTORY_MESSAGES
        )
        
        # Get AI response with found products
        ai_response, found_products, search_query = await assistant.get_response(
            user_message=user_text,
            chat_history=history[:-1],  # Exclude current message
            assistant_gender=assistant_gender
        )
        
        # Save assistant response to database
        await db.add_message(
            user_id=user.id,
            role="assistant",
            content=ai_response
        )
        
        # Check if products were found - add keyboard with numbered buttons + pagination
        keyboard = None
        if found_products:
            # Show only first 3 products
            top_3 = found_products[:3]
            total_found = len(found_products)
            
            keyboard = get_products_list_keyboard(
                products=top_3,
                total_found=total_found,
                current_offset=0,
                query=search_query
            )
            logger.info(f"Adding keyboard: showing 3 of {total_found} products")
        
        # Send response
        await message.answer(ai_response, reply_markup=keyboard)
        
        logger.info(f"Response sent to {user.id}: {len(ai_response)} characters")
    
    except Exception as e:
        logger.error(f"Error handling message from {user.id}: {e}")
        await message.answer(
            "😔 Извините, произошла ошибка. Попробуйте еще раз."
        )

