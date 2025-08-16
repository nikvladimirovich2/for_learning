#TOKEN = ':'
#CHANNEL_ID = '-' # channel with bot
#CHANNEL_ID = '' # my personal chat with bot
import requests
from bs4 import BeautifulSoup
import schedule
import time
import sqlite3
from telegram import Bot
import logging

# Настройки логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# URL сайта для парсинга
url = 'https://013info.rs/pancevo/'

# Токен вашего бота Telegram
TELEGRAM_TOKEN = ''

# ID вашего чата в Telegram
CHAT_ID = '-1002250474196'

# Создаем объект бота
bot = Bot(token=TELEGRAM_TOKEN)

# Создаем базу данных для хранения информации о последних новостях
conn = sqlite3.connect('news.db')
cursor = conn.cursor()

# Создаем таблицу для хранения информации о последних новостях
cursor.execute('''
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    link TEXT,
    content TEXT
)
''')
conn.commit()

def parse_news():
    logger.info("Начало парсинга новостей")

    # Получаем HTML-код страницы
    response = requests.get(url)
    html = response.text

    # Создаем объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Находим все новости на странице
    news_items = soup.find_all('div', class_='col articleContent')

    # Проверяем наличие новых новостей
    for news in news_items:
        title_tag = news.find('h3')
        if title_tag:
            title = title_tag.text.strip()
            link = title_tag.find('a')['href']
        else:
            title = "Заголовок не найден"
            link = "Ссылка не найдена"

        content_tag = news.find('div', class_='lead')
        if content_tag:
            content = content_tag.text.strip()
        else:
            content = "Текст новости не найден"

        # Проверяем, есть ли такая новость в базе данных
        cursor.execute('SELECT * FROM news WHERE title = ? AND link = ?', (title, link))
        if cursor.fetchone() is None:
            # Если новости нет в базе данных, добавляем её
            cursor.execute('INSERT INTO news (title, link, content) VALUES (?, ?, ?)', (title, link, content))
            conn.commit()

            # Отправляем информацию о новой новости в Telegram
            message = f"Заголовок: {title}\nТекст: {content}\nСсылка: {link}"
            bot.send_message(chat_id=CHAT_ID, text=message)
            logger.info(f"Отправлена новая новость: {title}")
        else:
            logger.info(f"Новость уже существует: {title}")

    logger.info("Завершение парсинга новостей")

def run_scheduler():
    # Запускаем парсинг новостей каждую минуту
    schedule.every(10).minutes.do(parse_news)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    logger.info("Запуск скрипта")
    run_scheduler()