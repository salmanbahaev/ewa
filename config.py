"""Configuration module for the bot"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (.env.local приоритетнее .env)
if Path(".env.local").exists():
    load_dotenv(".env.local")
else:
    load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if not exist
LOGS_DIR.mkdir(exist_ok=True)

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
if not TELEGRAM_BOT_TOKEN:
    # Allow empty token only in test mode
    import sys
    if "pytest" not in sys.modules:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env file")
    TELEGRAM_BOT_TOKEN = "test_token"

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    # Allow empty key only in test mode
    import sys
    if "pytest" not in sys.modules:
        raise ValueError("OPENAI_API_KEY is not set in .env file")
    OPENAI_API_KEY = "test_key"

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Database
DATABASE_PATH = DATA_DIR / os.getenv("DATABASE_PATH", "bot_database.db")

# Data files
CATALOG_PATH = DATA_DIR / "catalog.json"
COMPANY_PATH = DATA_DIR / "company.json"
BUSINESS_PATH = DATA_DIR / "business.json"
EVENTS_PATH = DATA_DIR / "events.json"
GEOGRAPHY_PATH = DATA_DIR / "geography.json"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))

# Bot settings
MAX_HISTORY_MESSAGES = 10  # Количество сообщений истории для контекста
CHAT_TYPING_DELAY = 1  # Задержка перед ответом (typing action)

