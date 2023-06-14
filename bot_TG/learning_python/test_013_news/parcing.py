from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from datetime import datetime
import time

url = "https://013info.rs/pancevo"  
response = requests.get(url)
html_content = response.text

time.sleep(5)

date_format = "%d.%m.%Y"

soup = BeautifulSoup(html_content, "html.parser")

# Нахождение нужных элементов на странице
news_articles = soup.find_all("article", class_="node node-article slide") 
article = news_articles[0]
base_url = 'https://013info.rs'

# Обработка найденных элементов
for article in news_articles:
    news_title = article.find("div", class_="box-vest").h3.text.strip() # заголовок
    date_article = article.find("div", class_="vest-dana").h6.text.strip() # дата новости
    date_article = date_article.replace(" ", "")[:-1]
    deep_url = article.find('a')['href'] 
    link = urljoin(base_url, deep_url) # ссылка на новость
    
    if date_article == datetime.now().date().strftime("%d.%m.%Y"):
        response_new = requests.get(link)
        content = response_new.text
        time.sleep(3)
        soup_deep = BeautifulSoup(content, "html.parser")
        start_div = soup_deep.find("div", class_="sharethis-inline-share-buttons")
        
        end_div = soup_deep.find("div", class_="mytags")

        # Извлекаем текст между элементами
        text_new = ""
        next_element = start_div.find_next()
        
        while next_element != end_div:
            text_new += next_element.get_text()
            next_element = next_element.find_next()
        print(text_new)
        print('---------------------')
