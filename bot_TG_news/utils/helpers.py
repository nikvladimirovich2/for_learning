import logging
import time
import hashlib
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)

def setup_logging(log_level: str = 'INFO', log_file: str = 'bot.log'):
    """Настраивает логирование"""
    import logging.handlers
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Хендлер для файла с ротацией
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Хендлер для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    logger.info(f"Логирование настроено: уровень={log_level}, файл={log_file}")

def rate_limit(calls: int = 1, period: int = 1):
    """Декоратор для ограничения частоты вызовов"""
    def decorator(func):
        last_reset = time.time()
        call_count = 0
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_reset, call_count
            now = time.time()
            
            if now - last_reset > period:
                last_reset = now
                call_count = 0
                
            if call_count >= calls:
                sleep_time = period - (now - last_reset)
                if sleep_time > 0:
                    logger.debug(f"Rate limit: ожидание {sleep_time:.2f} сек")
                    time.sleep(sleep_time)
                
            call_count += 1
            return func(*args, **kwargs)
        return wrapper
    return decorator

def health_check(database, telegram_service) -> bool:
    """Проверяет здоровье системы"""
    try:
        # Проверка базы данных
        stats = database.get_statistics()
        if not stats:
            logger.error("Не удалось получить статистику базы данных")
            return False
        
        # Проверка Telegram API
        if not telegram_service.test_connection():
            logger.error("Не удалось подключиться к Telegram API")
            return False
        
        logger.info("Health check пройден успешно")
        return True
        
    except Exception as e:
        logger.error(f"Health check не пройден: {e}")
        return False

def cleanup_old_data(database, days: int = 30):
    """Очищает старые данные"""
    try:
        database.cleanup_old_news(days)
        logger.info(f"Очистка данных старше {days} дней завершена")
    except Exception as e:
        logger.error(f"Ошибка при очистке старых данных: {e}")

def get_performance_metrics(func):
    """Декоратор для сбора метрик производительности"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = None
        
        try:
            # Попытка получить информацию о памяти (если доступно)
            try:
                import psutil
                process = psutil.Process()
                start_memory = process.memory_info().rss / 1024 / 1024  # MB
            except ImportError:
                pass
            
            result = func(*args, **kwargs)
            
            # Собираем метрики
            end_time = time.time()
            duration = end_time - start_time
            
            if start_memory is not None:
                try:
                    end_memory = process.memory_info().rss / 1024 / 1024
                    memory_diff = end_memory - start_memory
                    logger.info(f"Функция {func.__name__}: время={duration:.2f}с, память={memory_diff:+.1f}MB")
                except:
                    logger.info(f"Функция {func.__name__}: время={duration:.2f}с")
            else:
                logger.info(f"Функция {func.__name__}: время={duration:.2f}с")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            logger.error(f"Функция {func.__name__} завершилась с ошибкой за {duration:.2f}с: {e}")
            raise
    
    return wrapper

def validate_news_data(news_data: Dict) -> bool:
    """Проверяет корректность данных новости"""
    required_fields = ['title', 'link', 'content']
    
    for field in required_fields:
        if not news_data.get(field):
            logger.warning(f"Отсутствует обязательное поле: {field}")
            return False
    
    # Проверяем длину заголовка
    if len(news_data['title']) < 5:
        logger.warning("Заголовок слишком короткий")
        return False
    
    # Проверяем длину контента
    if len(news_data['content']) < 10:
        logger.warning("Контент слишком короткий")
        return False
    
    # Проверяем корректность URL
    if not news_data['link'].startswith('http'):
        logger.warning("Некорректный URL")
        return False
    
    return True

def sanitize_text(text: str) -> str:
    """Очищает текст от лишних символов"""
    if not text:
        return ""
    
    # Убираем лишние пробелы и переносы строк
    text = ' '.join(text.split())
    
    # Экранируем специальные символы для Markdown
    special_chars = ['*', '_', '`', '[', ']', '(', ')', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def format_timestamp(timestamp: str) -> str:
    """Форматирует временную метку"""
    try:
        # Пытаемся распарсить различные форматы времени
        formats = [
            '%d.%m.%Y. | %H:%M',
            '%d.%m.%Y.',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp, fmt)
                return dt.strftime('%d.%m.%Y %H:%M')
            except ValueError:
                continue
        
        # Если не удалось распарсить, возвращаем как есть
        return timestamp
        
    except Exception as e:
        logger.error(f"Ошибка форматирования времени '{timestamp}': {e}")
        return timestamp

def calculate_hash(data: str) -> str:
    """Вычисляет хеш данных"""
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def is_working_hours() -> bool:
    """Проверяет, рабочее ли сейчас время"""
    now = datetime.now()
    
    # Рабочие часы: 8:00 - 22:00
    start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=22, minute=0, second=0, microsecond=0)
    
    return start_time <= now <= end_time

def get_next_run_time(interval_minutes: int) -> datetime:
    """Вычисляет время следующего запуска"""
    now = datetime.now()
    next_run = now + timedelta(minutes=interval_minutes)
    
    # Если сейчас нерабочее время, переносим на утро
    if not is_working_hours():
        next_run = next_run.replace(hour=8, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
    
    return next_run
