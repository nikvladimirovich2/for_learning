import os
from dotenv import load_dotenv
from pathlib import Path

# Определяем путь к .env файлу
env_path = Path(__file__).parent.parent / '.env'

# Загружаем переменные окружения
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Загружен .env файл: {env_path}")
else:
    print(f"⚠️ .env файл не найден: {env_path}")
    print("Используются значения по умолчанию")

# Основные настройки
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
CHAT_ID = os.getenv('CHAT_ID', '-1002250474196')
NEWS_URL = os.getenv('NEWS_URL', 'https://013info.rs/pancevo/')
PARSING_INTERVAL = int(os.getenv('PARSING_INTERVAL', 10))
MAX_PAGES = int(os.getenv('MAX_PAGES', 3))

# Настройки логирования
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')

# Настройки парсинга
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
REQUEST_DELAY = int(os.getenv('REQUEST_DELAY', 1))
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 200))

# Настройки фильтрации
EXCLUDED_CATEGORIES = os.getenv('EXCLUDED_CATEGORIES', 'marketing').split(',') if os.getenv('EXCLUDED_CATEGORIES') else ['marketing']
EXCLUDED_KEYWORDS = os.getenv('EXCLUDED_KEYWORDS', 'reklama,oglas,sponzor,reklamni').split(',') if os.getenv('EXCLUDED_KEYWORDS') else ['reklama', 'oglas', 'sponzor', 'reklamni']

# Настройки базы данных
DATABASE_FILE = os.getenv('DATABASE_FILE', 'news.db')

# Настройки Telegram
TELEGRAM_PARSE_MODE = 'Markdown'
TELEGRAM_DISABLE_WEB_PAGE_PREVIEW = True

# Проверка обязательных настроек
def validate_config():
    """Проверяет корректность конфигурации"""
    errors = []
    
    if not TELEGRAM_TOKEN:
        errors.append("TELEGRAM_TOKEN не установлен")
    
    if not CHAT_ID:
        errors.append("CHAT_ID не установлен")
    
    if errors:
        print("❌ Ошибки конфигурации:")
        for error in errors:
            print(f"   - {error}")
        print("\nСоздайте .env файл на основе env_example.txt")
        return False
    
    print("✅ Конфигурация загружена успешно")
    return True

# Проверяем конфигурацию при импорте
if __name__ == "__main__":
    validate_config()
else:
    # При импорте модуля только выводим предупреждение
    if not TELEGRAM_TOKEN:
        print("⚠️ TELEGRAM_TOKEN не установлен. Создайте .env файл")
