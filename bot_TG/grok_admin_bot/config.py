# Configuration file for ChatGPT Telegram Bot
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# OpenAI ChatGPT API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-3.5-turbo"  # or "gpt-4" for better quality

# Channel Management
ADMIN_CHANNEL_ID = os.getenv("ADMIN_CHANNEL_ID", "")
PUBLIC_CHANNEL_ID = os.getenv("PUBLIC_CHANNEL_ID", "")

# Bot Settings
MAX_COMMENT_LENGTH = 1000
MAX_ARTICLE_LENGTH = 4000
COMMENT_RESPONSE_TIMEOUT = 30  # seconds
ARTICLE_GENERATION_TIMEOUT = 120  # seconds

# Popular Topics for Article Generation
DEFAULT_TOPICS = [
    "artificial intelligence trends",
    "cryptocurrency news",
    "technology innovations",
    "scientific discoveries",
    "business insights",
    "health and wellness",
    "environmental news",
    "space exploration"
]

# Language Settings
DEFAULT_LANGUAGE = "en"  # en, ru, etc.
SUPPORTED_LANGUAGES = ["en", "ru"]

# Error Messages
ERROR_MESSAGES = {
    "en": {
        "api_error": "Sorry, I'm experiencing technical difficulties. Please try again later.",
        "permission_denied": "You don't have permission to perform this action.",
        "invalid_input": "Invalid input. Please check your request and try again."
    },
    "ru": {
        "api_error": "Извините, у меня технические проблемы. Попробуйте позже.",
        "permission_denied": "У вас нет прав для выполнения этого действия.",
        "invalid_input": "Неверный ввод. Проверьте ваш запрос и попробуйте снова."
    }
}
