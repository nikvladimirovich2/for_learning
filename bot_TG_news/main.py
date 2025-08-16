#!/usr/bin/env python3
"""
Новостной бот для Telegram
Парсит новости с сайта 013info.rs и отправляет их в канал
"""

import schedule
import time
import logging
from datetime import datetime
from typing import List, Dict

# Импорты наших модулей
from config.settings import (
    TELEGRAM_TOKEN, CHAT_ID, NEWS_URL, PARSING_INTERVAL,
    LOG_LEVEL, LOG_FILE
)
from database.models import NewsDatabase
from services.news_parser import NewsParser
from services.telegram_service import TelegramService
from utils.helpers import (
    setup_logging, health_check, cleanup_old_data,
    get_performance_metrics, validate_news_data
)

# Настраиваем логирование
setup_logging(LOG_LEVEL, LOG_FILE)
logger = logging.getLogger(__name__)

class NewsBot:
    def __init__(self):
        """Инициализация бота"""
        self.database = None
        self.parser = None
        self.telegram = None
        self.is_running = False
        
        logger.info("Инициализация новостного бота")
        
        # Проверяем обязательные настройки
        if not TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN не установлен")
        if not CHAT_ID:
            raise ValueError("CHAT_ID не установлен")
        
        # Инициализируем компоненты
        self._init_components()
        
        logger.info("Новостной бот инициализирован успешно")
    
    def _init_components(self):
        """Инициализирует все компоненты бота"""
        try:
            # База данных
            self.database = NewsDatabase()
            logger.info("База данных инициализирована")
            
            # Парсер новостей
            self.parser = NewsParser(NEWS_URL)
            logger.info("Парсер новостей инициализирован")
            
            # Telegram сервис
            self.telegram = TelegramService(TELEGRAM_TOKEN)
            logger.info("Telegram сервис инициализирован")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации компонентов: {e}")
            raise
    
    @get_performance_metrics
    def parse_and_send_news(self):
        """Основная функция парсинга и отправки новостей"""
        try:
            logger.info("Начало цикла парсинга новостей")
            
            # Проверяем здоровье системы
            if not health_check(self.database, self.telegram):
                logger.error("Health check не пройден, пропускаем цикл")
                return
            
            # Парсим новости
            news_list = self.parser.get_all_news_pages()
            
            if not news_list:
                logger.info("Новых новостей не найдено")
                return
            
            logger.info(f"Найдено {len(news_list)} новостей")
            
            # Обрабатываем каждую новость
            new_news_count = 0
            sent_news_count = 0
            
            for news_data in news_list:
                try:
                    # Валидируем данные
                    if not validate_news_data(news_data):
                        logger.warning(f"Некорректные данные новости: {news_data.get('title', 'Unknown')}")
                        continue
                    
                    # Добавляем в базу данных
                    if self.database.add_news(
                        title=news_data['title'],
                        link=news_data['link'],
                        content=news_data['content'],
                        date=news_data.get('date'),
                        category=news_data.get('category'),
                        image_url=news_data.get('image_url')
                    ):
                        new_news_count += 1
                        
                        # Отправляем новость в Telegram
                        if self.telegram.send_news(CHAT_ID, news_data):
                            sent_news_count += 1
                            logger.info(f"Новость отправлена: {news_data['title']}")
                        else:
                            logger.error(f"Не удалось отправить новость: {news_data['title']}")
                    
                except Exception as e:
                    logger.error(f"Ошибка обработки новости: {e}")
                    continue
            
            logger.info(f"Цикл завершен: {new_news_count} новых, {sent_news_count} отправлено")
            
        except Exception as e:
            logger.error(f"Критическая ошибка в цикле парсинга: {e}")
            # Отправляем уведомление об ошибке
            try:
                self.telegram.send_error_notification(CHAT_ID, str(e))
            except:
                pass
    
    def send_daily_digest(self):
        """Отправляет ежедневный дайджест"""
        try:
            logger.info("Отправка ежедневного дайджеста")
            
            digest_data = self.database.get_daily_digest()
            if digest_data:
                self.telegram.send_daily_digest(CHAT_ID, digest_data)
            else:
                logger.info("Нет данных для ежедневного дайджеста")
                
        except Exception as e:
            logger.error(f"Ошибка отправки ежедневного дайджеста: {e}")
    
    def send_statistics(self):
        """Отправляет статистику бота"""
        try:
            logger.info("Отправка статистики")
            
            stats = self.database.get_statistics()
            if stats:
                self.telegram.send_statistics(CHAT_ID, stats)
            else:
                logger.warning("Не удалось получить статистику")
                
        except Exception as e:
            logger.error(f"Ошибка отправки статистики: {e}")
    
    def cleanup_old_data(self):
        """Очищает старые данные"""
        try:
            logger.info("Очистка старых данных")
            cleanup_old_data(self.database, days=30)
        except Exception as e:
            logger.error(f"Ошибка очистки старых данных: {e}")
    
    def setup_scheduler(self):
        """Настраивает планировщик задач"""
        try:
            # Основной цикл парсинга
            schedule.every(PARSING_INTERVAL).minutes.do(self.parse_and_send_news)
            
            # Ежедневный дайджест в 9:00
            schedule.every().day.at("09:00").do(self.send_daily_digest)
            
            # Статистика каждый день в 18:00
            schedule.every().day.at("18:00").do(self.send_statistics)
            
            # Очистка старых данных каждый день в 3:00
            schedule.every().day.at("03:00").do(self.cleanup_old_data)
            
            logger.info("Планировщик настроен")
            
        except Exception as e:
            logger.error(f"Ошибка настройки планировщика: {e}")
            raise
    
    def run(self):
        """Запускает бота"""
        try:
            logger.info("Запуск новостного бота")
            
            # Настраиваем планировщик
            self.setup_scheduler()
            
            # Отправляем сообщение о запуске
            self.telegram.send_message(
                CHAT_ID,
                "🚀 **Новостной бот запущен**\n\nБот будет автоматически парсить новости и отправлять их в канал."
            )
            
            self.is_running = True
            
            # Основной цикл
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Получен сигнал остановки")
                    break
                except Exception as e:
                    logger.error(f"Ошибка в основном цикле: {e}")
                    time.sleep(60)  # Ждем минуту перед повторной попыткой
            
        except Exception as e:
            logger.error(f"Критическая ошибка запуска бота: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self):
        """Останавливает бота"""
        try:
            logger.info("Остановка новостного бота")
            
            self.is_running = False
            
            # Отправляем сообщение об остановке
            try:
                self.telegram.send_message(
                    CHAT_ID,
                    "🛑 **Новостной бот остановлен**"
                )
            except:
                pass
            
            # Закрываем соединения
            if self.database:
                self.database.close()
            if self.parser:
                self.parser.close()
            
            logger.info("Бот остановлен")
            
        except Exception as e:
            logger.error(f"Ошибка при остановке бота: {e}")

def main():
    """Главная функция"""
    bot = None
    
    try:
        # Создаем и запускаем бота
        bot = NewsBot()
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Программа остановлена пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        
        # Отправляем уведомление об ошибке если возможно
        if bot and bot.telegram:
            try:
                bot.telegram.send_error_notification(CHAT_ID, str(e))
            except:
                pass
    finally:
        # Останавливаем бота
        if bot:
            bot.stop()

if __name__ == '__main__':
    main()