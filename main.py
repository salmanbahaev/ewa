"""Main entry point for EWA Product Telegram Bot"""
import asyncio
import sys
from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
from data.database import Database
from ai.assistant import AIAssistant
from bot.handlers import start, messages, callbacks, menu, clear, menu_buttons, product_card
from bot.middlewares.logging import LoggingMiddleware


async def main():
    """Main function to start the bot"""
    
    # Configure logging
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=config.LOG_LEVEL
    )
    logger.add(
        config.LOG_DIR / "bot_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=config.LOG_LEVEL
    )
    
    logger.info("=" * 50)
    logger.info("Starting EWA Product Telegram Bot")
    logger.info("=" * 50)
    
    # Initialize database
    db = Database(config.DATABASE_PATH)
    await db.init_db()
    logger.info("Database initialized")
    
    # Initialize AI Assistant
    assistant = AIAssistant()
    logger.info("AI Assistant initialized")
    
    # Initialize bot
    # Если нужен прокси (для России), раскомментируй следующие строки:
    # from aiogram.client.session.aiohttp import AiohttpSession
    # session = AiohttpSession(proxy="http://proxy_address:port")
    # bot = Bot(token=config.TELEGRAM_BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    
    bot = Bot(
        token=config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    logger.info("Bot initialized")
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Add middleware
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    logger.info("Middleware registered")
    
    # Register routers
    dp.include_router(start.router)
    dp.include_router(clear.router)
    dp.include_router(menu.router)
    dp.include_router(menu_buttons.router)  # Reply keyboard buttons
    dp.include_router(product_card.router)  # Product cards with photos
    dp.include_router(callbacks.router)
    dp.include_router(messages.router)  # Messages должен быть последним
    logger.info("Handlers registered")
    
    # Inject dependencies
    dp["db"] = db
    dp["assistant"] = assistant
    
    # Start polling
    try:
        logger.info("Starting polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Error during polling: {e}")
    finally:
        await bot.session.close()
        await db.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

