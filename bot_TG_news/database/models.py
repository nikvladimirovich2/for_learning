import sqlite3
import hashlib
import logging
from datetime import datetime
from typing import Optional, List, Tuple
from config.settings import DATABASE_FILE

logger = logging.getLogger(__name__)

class NewsDatabase:
    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self.init_database()
    
    def init_database(self):
        """Инициализирует базу данных и создает таблицы"""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            self.create_tables()
            logger.info("База данных инициализирована успешно")
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def create_tables(self):
        """Создает таблицы в базе данных"""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    link TEXT UNIQUE NOT NULL,
                    content TEXT,
                    date TEXT,
                    category TEXT,
                    image_url TEXT,
                    hash TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sent_at TIMESTAMP,
                    is_sent BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Создаем индексы для быстрого поиска
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_link ON news(link)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_hash ON news(hash)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_sent ON news(is_sent)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON news(created_at)')
            
            self.conn.commit()
            logger.info("Таблицы созданы успешно")
        except Exception as e:
            logger.error(f"Ошибка создания таблиц: {e}")
            raise
    
    def generate_news_hash(self, title: str, content: str, link: str) -> str:
        """Генерирует хеш для новости"""
        content_to_hash = f"{title}{content}{link}"
        return hashlib.md5(content_to_hash.encode('utf-8')).hexdigest()
    
    def news_exists(self, hash_value: str) -> bool:
        """Проверяет, существует ли новость с таким хешем"""
        try:
            self.cursor.execute('SELECT 1 FROM news WHERE hash = ?', (hash_value,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Ошибка проверки существования новости: {e}")
            return False
    
    def add_news(self, title: str, link: str, content: str, date: str = None, 
                 category: str = None, image_url: str = None) -> bool:
        """Добавляет новую новость в базу данных"""
        try:
            hash_value = self.generate_news_hash(title, content, link)
            
            if self.news_exists(hash_value):
                logger.info(f"Новость уже существует: {title}")
                return False
            
            self.cursor.execute('''
                INSERT INTO news (title, link, content, date, category, image_url, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, link, content, date, category, image_url, hash_value))
            
            self.conn.commit()
            logger.info(f"Новость добавлена: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления новости: {e}")
            return False
    
    def get_unsent_news(self, limit: int = 10) -> List[Tuple]:
        """Получает неотправленные новости"""
        try:
            self.cursor.execute('''
                SELECT id, title, link, content, date, category, image_url, hash
                FROM news 
                WHERE is_sent = FALSE 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка получения неотправленных новостей: {e}")
            return []
    
    def mark_as_sent(self, news_id: int):
        """Отмечает новость как отправленную"""
        try:
            self.cursor.execute('''
                UPDATE news 
                SET is_sent = TRUE, sent_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (news_id,))
            self.conn.commit()
            logger.info(f"Новость {news_id} отмечена как отправленная")
        except Exception as e:
            logger.error(f"Ошибка отметки новости как отправленной: {e}")
    
    def get_statistics(self) -> dict:
        """Получает статистику по новостям"""
        try:
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as total_news,
                    COUNT(CASE WHEN is_sent = TRUE THEN 1 END) as sent_news,
                    COUNT(CASE WHEN is_sent = FALSE THEN 1 END) as unsent_news,
                    COUNT(DISTINCT DATE(created_at)) as days_active,
                    MAX(created_at) as last_news,
                    MAX(sent_at) as last_sent
                FROM news
            ''')
            
            result = self.cursor.fetchone()
            return {
                'total_news': result[0],
                'sent_news': result[1],
                'unsent_news': result[2],
                'days_active': result[3],
                'last_news': result[4],
                'last_sent': result[5]
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}
    
    def get_daily_digest(self) -> List[Tuple]:
        """Получает новости для ежедневного дайджеста"""
        try:
            self.cursor.execute('''
                SELECT category, COUNT(*) as count, 
                       GROUP_CONCAT(title, ' | ') as titles
                FROM news 
                WHERE DATE(created_at) = DATE('now') AND is_sent = FALSE
                GROUP BY category
            ''')
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка получения ежедневного дайджеста: {e}")
            return []
    
    def cleanup_old_news(self, days: int = 30):
        """Удаляет старые новости"""
        try:
            self.cursor.execute('''
                DELETE FROM news 
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            
            deleted_count = self.cursor.rowcount
            self.conn.commit()
            logger.info(f"Удалено {deleted_count} старых новостей")
        except Exception as e:
            logger.error(f"Ошибка очистки старых новостей: {e}")
    
    def close(self):
        """Закрывает соединение с базой данных"""
        if self.conn:
            self.conn.close()
            logger.info("Соединение с базой данных закрыто")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
