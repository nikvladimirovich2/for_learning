import requests
import time
import logging
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from functools import wraps
from config.settings import (
    REQUEST_TIMEOUT, REQUEST_DELAY, MAX_PAGES, 
    EXCLUDED_CATEGORIES, EXCLUDED_KEYWORDS
)

logger = logging.getLogger(__name__)

def retry_on_failure(max_retries=3, delay=5):
    """Декоратор для повторных попыток при ошибках"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Финальная ошибка после {max_retries} попыток: {e}")
                        raise
                    logger.warning(f"Попытка {attempt + 1} не удалась: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

class NewsParser:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_news_image(self, news_item) -> Optional[str]:
        """Получает URL изображения новости"""
        try:
            img_tag = news_item.find('img', class_='wp-post-image')
            if img_tag:
                # Получаем лучшее качество изображения
                srcset = img_tag.get('srcset')
                if srcset:
                    # Берем изображение с максимальным разрешением
                    urls = [url.strip().split(' ')[0] for url in srcset.split(',')]
                    return urls[-1] if urls else img_tag.get('src')
                return img_tag.get('src')
            return None
        except Exception as e:
            logger.error(f"Ошибка получения изображения: {e}")
            return None
    
    def extract_category_from_url(self, url: str) -> str:
        """Извлекает категорию из URL новости"""
        try:
            # Пример URL: https://013info.rs/pancevo/drustvo/news-title/
            parts = url.split('/')
            if len(parts) > 4:
                return parts[4]  # drustvo, ekonomija, sport и т.д.
            return 'general'
        except Exception as e:
            logger.error(f"Ошибка извлечения категории: {e}")
            return 'general'
    
    def should_send_news(self, category: str, title: str, content: str) -> bool:
        """Определяет, стоит ли отправлять новость"""
        try:
            # Исключаем определенные категории
            if category.lower() in [cat.lower() for cat in EXCLUDED_CATEGORIES]:
                return False
            
            # Проверяем ключевые слова
            text = f"{title} {content}".lower()
            if any(keyword.lower() in text for keyword in EXCLUDED_KEYWORDS):
                return False
            
            return True
        except Exception as e:
            logger.error(f"Ошибка проверки новости: {e}")
            return True  # В случае ошибки отправляем новость
    
    def parse_news_item(self, news_item) -> Optional[Dict]:
        """Парсит отдельную новость"""
        try:
            # Заголовок
            title_tag = news_item.find('h3')
            if not title_tag:
                return None
            
            title = title_tag.get_text(strip=True)
            if not title:
                return None
            
            # Ссылка
            link_tag = title_tag.find('a')
            if not link_tag or not link_tag.get('href'):
                return None
            
            link = link_tag['href']
            
            # Краткое описание
            content_tag = news_item.find('div', class_='lead')
            content = content_tag.get_text(strip=True) if content_tag else ""
            
            # Дата публикации
            date_tag = news_item.find('div', class_='articleMeta')
            date = date_tag.get_text(strip=True) if date_tag else ""
            
            # Изображение
            image_url = self.get_news_image(news_item)
            
            # Категория
            category = self.extract_category_from_url(link)
            
            # Проверяем, стоит ли отправлять новость
            if not self.should_send_news(category, title, content):
                logger.info(f"Новость отфильтрована: {title}")
                return None
            
            return {
                'title': title,
                'link': link,
                'content': content,
                'date': date,
                'category': category,
                'image_url': image_url
            }
            
        except Exception as e:
            logger.error(f"Ошибка парсинга новости: {e}")
            return None
    
    @retry_on_failure(max_retries=3, delay=5)
    def parse_page(self, url: str) -> List[Dict]:
        """Парсит одну страницу новостей"""
        try:
            logger.info(f"Парсинг страницы: {url}")
            
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Находим все новости на странице
            news_items = soup.find_all('article', class_='post')
            
            if not news_items:
                logger.warning(f"На странице {url} не найдено новостей")
                return []
            
            parsed_news = []
            for news in news_items:
                news_data = self.parse_news_item(news)
                if news_data:
                    parsed_news.append(news_data)
            
            logger.info(f"Страница {url}: найдено {len(parsed_news)} новостей")
            return parsed_news
            
        except requests.RequestException as e:
            logger.error(f"Ошибка HTTP запроса к {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при парсинге {url}: {e}")
            raise
    
    def get_all_news_pages(self, max_pages: int = MAX_PAGES) -> List[Dict]:
        """Получает новости с нескольких страниц"""
        all_news = []
        
        for page in range(1, max_pages + 1):
            try:
                if page == 1:
                    url = self.base_url
                else:
                    url = f"{self.base_url}strana/{page}/"
                
                page_news = self.parse_page(url)
                all_news.extend(page_news)
                
                # Задержка между запросами
                if page < max_pages:
                    time.sleep(REQUEST_DELAY)
                
            except Exception as e:
                logger.error(f"Ошибка при получении страницы {page}: {e}")
                break
        
        logger.info(f"Всего найдено новостей: {len(all_news)}")
        return all_news
    
    def track_parsing_performance(self, func):
        """Декоратор для отслеживания производительности парсинга"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            news_count = 0
            
            try:
                result = func(*args, **kwargs)
                news_count = len(result) if isinstance(result, list) else 0
                return result
            finally:
                end_time = time.time()
                duration = end_time - start_time
                
                logger.info(f"Парсинг завершен: {news_count} новостей за {duration:.2f} секунд")
                
                # Предупреждение о медленном парсинге
                if duration > 60:
                    logger.warning(f"Медленный парсинг: {duration:.2f} сек для {news_count} новостей")
        
        return wrapper
    
    def close(self):
        """Закрывает сессию"""
        if self.session:
            self.session.close()
            logger.info("Сессия парсера закрыта")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
