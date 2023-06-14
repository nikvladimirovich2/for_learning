# Импортируем необходимые модули
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Определяем переменные для вставок
url = "https://www.linkedin.com/"
search_query = "linux administrator"

# Запускаем браузер и открываем страницу
driver = webdriver.Chrome("--incognito")
# driver.add_argument("--incognito")

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--incognito")
# driver = webdriver.Chrome(chrome_options=chrome_options)

driver.get(url)

time.sleep(3)

# Находим элементы для ввода логина и пароля
username_box = driver.find_element("xpath", "//input[@id='session_key']")
#password_box = driver.find_element_by_xpath("//input[@name='password']")
password_box = driver.find_element("xpath", "//input[@id='session_password']")

# Вводим данные для авторизации
username_box.send_keys("nikvladimirovich2@gmail.com")
password_box.send_keys("nekitbljat")

# Отправляем форму авторизации
password_box.submit()

time.sleep(3)

# Находим элемент поисковой строки и вводим запрос
# search_box = driver.find_element('xpath', '//*[@id="global-nav-typeahead"]/input')
# search_box.send_keys(search_query)
# search_box.send_keys(Keys.RETURN)

# Дождаться загрузки страницы профиля
profile_link = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.LINK_TEXT, 'My Network'))
)

# Перейти на страницу "Моя сеть"
profile_link.click()
time.sleep(3)
# Дождаться загрузки страницы "Моя сеть"
# network_link = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.LINK_TEXT, 'Connections'))
# )

network_link = driver.find_element('xpath', '/html/body/div[5]/div[3]/div/div/div/div/div[2]/div/div/div/div/div/div/section[1]/div/div[1]/a/div/div[1]')

# Перейти на страницу "Мои контакты"
network_link.click()
time.sleep(3)

link_search = driver.find_element('xpath', '/html/body/div[5]/div[3]/div/div/div/div/div[2]/div/div/main/div/section/div[1]/div[2]/a')
link_search.click()
time.sleep(3)

# Применить фильтры (страна и языки)
filter_button = driver.find_element('xpath', '/html/body/div[5]/div[3]/div[2]/section/div/nav/div/div/div/button')
filter_button.click()
time.sleep(3)

# Выбрать фильтр по стране
country_filter = driver.find_element('xpath', '//input[@name="locations-filter-value"]')
country_filter.send_keys('Russia')
country_filter.send_keys(Keys.ENTER)

# Выбрать фильтр по языку
language_filter = driver.find_element('xpath', '//input[@name="profile-language-filter-value"]')
language_filter.send_keys('English')
language_filter.send_keys(Keys.ENTER)
language_filter.send_keys('Russian')
language_filter.send_keys(Keys.ENTER)

show_results_button = driver.find_element('xpath', '/html/body/div[3]/div/div/div[3]/div/button[2]')
show_results_button.click()

time.sleep(10)

# Проходимся по каждому элементу и выводим его описание
# for result in results:
#     title = result.find_element_by_xpath(".//h3").text
#     description = result.find_element_by_xpath(".//p").text
#     print(f"Title: {title}")
#     print(f"Description: {description}")
    
# Закрываем браузер
#driver.quit()