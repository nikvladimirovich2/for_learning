import logging
import time
from typing import Optional, Dict, List
from telegram import Bot, ParseMode
from telegram.error import TelegramError, RetryAfter
from config.settings import (
    TELEGRAM_TOKEN, TELEGRAM_PARSE_MODE, 
    TELEGRAM_DISABLE_WEB_PAGE_PREVIEW, MAX_CONTENT_LENGTH
)

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, token: str = TELEGRAM_TOKEN):
        self.bot = Bot(token=token)
        self.parse_mode = ParseMode.MARKDOWN
        self.disable_web_page_preview = TELEGRAM_DISABLE_WEB_PAGE_PREVIEW
    
    def format_news_message(self, title: str, content: str, link: str, 
                           date: str = None, category: str = None) -> str:
        """Форматирует новость для отправки в Telegram"""
        
        # Эмодзи для категорий
        category_emojis = {
            'drustvo': '🏛️',
            'ekonomija': '💰',
            'zdravstvo': '🏥',
            'ekologija': '🌱',
            'politika': '🗳️',
            'hronika': '📰',
            'servisne-informacije': '🔧',
            'kultura': '🎭',
            'sport': '⚽',
            'najave-dogadjaja': '📅',
            'general': '📰'
        }
        
        # Определяем эмодзи категории
        category_emoji = category_emojis.get(category.lower(), '📰')
        
        # Формируем сообщение
        message_parts = []
        
        # Заголовок с эмодзи категории
        message_parts.append(f"{category_emoji} **{title}**")
        
        # Дата
        if date:
            message_parts.append(f"📅 {date}")
        
        # Краткое описание
        if content:
            # Обрезаем контент если он слишком длинный
            truncated_content = content[:MAX_CONTENT_LENGTH]
            if len(content) > MAX_CONTENT_LENGTH:
                truncated_content += "..."
            message_parts.append(f"📝 {truncated_content}")
        
        # Ссылка
        message_parts.append(f"🔗 [Читать далее]({link})")
        
        return "\n\n".join(message_parts)
    
    def send_news_message(self, chat_id: str, title: str, content: str, 
                         link: str, date: str = None, category: str = None) -> bool:
        """Отправляет текстовое сообщение с новостью"""
        try:
            message = self.format_news_message(title, content, link, date, category)
            
            self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=self.parse_mode,
                disable_web_page_preview=self.disable_web_page_preview
            )
            
            logger.info(f"Отправлено текстовое сообщение: {title}")
            return True
            
        except RetryAfter as e:
            logger.warning(f"Telegram требует задержку: {e.retry_after} сек")
            time.sleep(e.retry_after)
            return self.send_news_message(chat_id, title, content, link, date, category)
            
        except TelegramError as e:
            logger.error(f"Ошибка Telegram при отправке текста: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке текста: {e}")
            return False
    
    def send_news_with_image(self, chat_id: str, title: str, content: str, 
                            link: str, image_url: str, date: str = None, 
                            category: str = None) -> bool:
        """Отправляет новость с изображением"""
        try:
            message = self.format_news_message(title, content, link, date, category)
            
            self.bot.send_photo(
                chat_id=chat_id,
                photo=image_url,
                caption=message,
                parse_mode=self.parse_mode
            )
            
            logger.info(f"Отправлено сообщение с изображением: {title}")
            return True
            
        except RetryAfter as e:
            logger.warning(f"Telegram требует задержку: {e.retry_after} сек")
            time.sleep(e.retry_after)
            return self.send_news_with_image(chat_id, title, content, link, image_url, date, category)
            
        except TelegramError as e:
            logger.error(f"Ошибка Telegram при отправке изображения: {e}")
            # Пробуем отправить без изображения
            return self.send_news_message(chat_id, title, content, link, date, category)
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке изображения: {e}")
            # Пробуем отправить без изображения
            return self.send_news_message(chat_id, title, content, link, date, category)
    
    def send_news(self, chat_id: str, news_data: Dict) -> bool:
        """Отправляет новость в зависимости от наличия изображения"""
        try:
            title = news_data.get('title', '')
            content = news_data.get('content', '')
            link = news_data.get('link', '')
            date = news_data.get('date', '')
            category = news_data.get('category', '')
            image_url = news_data.get('image_url', '')
            
            if image_url:
                return self.send_news_with_image(
                    chat_id, title, content, link, image_url, date, category
                )
            else:
                return self.send_news_message(
                    chat_id, title, content, link, date, category
                )
                
        except Exception as e:
            logger.error(f"Ошибка при отправке новости: {e}")
            return False
    
    def send_daily_digest(self, chat_id: str, digest_data: List[tuple]) -> bool:
        """Отправляет ежедневный дайджест новостей"""
        try:
            if not digest_data:
                logger.info("Нет данных для ежедневного дайджеста")
                return True
            
            digest = "📰 **Ежедневный дайджест новостей**\n\n"
            
            for category, count, titles in digest_data:
                # Определяем эмодзи категории
                category_emojis = {
                    'drustvo': '🏛️', 'ekonomija': '💰', 'zdravstvo': '🏥',
                    'ekologija': '🌱', 'politika': '🗳️', 'hronika': '📰',
                    'servisne-informacije': '🔧', 'kultura': '🎭', 'sport': '⚽',
                    'najave-dogadjaja': '📅', 'general': '📰'
                }
                
                emoji = category_emojis.get(category.lower(), '📰')
                digest += f"{emoji} **{category.title()}** ({count}):\n"
                
                # Обрезаем заголовки если их много
                if len(titles) > 150:
                    titles = titles[:150] + "..."
                digest += f"{titles}\n\n"
            
            self.bot.send_message(
                chat_id=chat_id,
                text=digest,
                parse_mode=self.parse_mode
            )
            
            logger.info("Ежедневный дайджест отправлен")
            return True
            
        except RetryAfter as e:
            logger.warning(f"Telegram требует задержку: {e.retry_after} сек")
            time.sleep(e.retry_after)
            return self.send_daily_digest(chat_id, digest_data)
            
        except TelegramError as e:
            logger.error(f"Ошибка Telegram при отправке дайджеста: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке дайджеста: {e}")
            return False
    
    def send_statistics(self, chat_id: str, stats: Dict) -> bool:
        """Отправляет статистику бота"""
        try:
            stats_message = f"""
📊 **Статистика новостного бота**

📰 Всего новостей: {stats.get('total_news', 0)}
✅ Отправлено: {stats.get('sent_news', 0)}
⏳ Ожидают отправки: {stats.get('unsent_news', 0)}
📅 Дней активности: {stats.get('days_active', 0)}
🕐 Последняя новость: {stats.get('last_news', 'Нет данных')}
📤 Последняя отправка: {stats.get('last_sent', 'Нет данных')}
            """.strip()
            
            self.bot.send_message(
                chat_id=chat_id,
                text=stats_message,
                parse_mode=self.parse_mode
            )
            
            logger.info("Статистика отправлена")
            return True
            
        except RetryAfter as e:
            logger.warning(f"Telegram требует задержку: {e.retry_after} сек")
            time.sleep(e.retry_after)
            return self.send_statistics(chat_id, stats)
            
        except TelegramError as e:
            logger.error(f"Ошибка Telegram при отправке статистики: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке статистики: {e}")
            return False
    
    def send_error_notification(self, chat_id: str, error_message: str) -> bool:
        """Отправляет уведомление об ошибке"""
        try:
            message = f"⚠️ **Ошибка в работе бота**\n\n{error_message}"
            
            self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=self.parse_mode
            )
            
            logger.info("Уведомление об ошибке отправлено")
            return True
            
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление об ошибке: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Проверяет соединение с Telegram API"""
        try:
            bot_info = self.bot.get_me()
            logger.info(f"Подключение к Telegram успешно: {bot_info.first_name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к Telegram: {e}")
            return False
