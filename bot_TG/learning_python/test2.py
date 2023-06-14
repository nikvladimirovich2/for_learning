import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Создание опций для режима инкогнито
options = Options()
options.add_argument("--incognito")

# Инициализация драйвера
driver = webdriver.Chrome(options=options)

# Открытие LinkedIn
driver.get("https://www.linkedin.com")

# Логин (необходимо заменить на ваши учетные данные)
username = ""
password = ""

# Ввод логина
time.sleep(3)
username_input = driver.find_element(By.ID, "session_key")
username_input.send_keys(username)

# Ввод пароля
password_input = driver.find_element(By.ID, "session_password")
password_input.send_keys(password)

# Нажатие на кнопку Войти
sign_in_button = driver.find_element(By.XPATH, "//button[@type='submit']")
sign_in_button.click()

# Переход на вкладку "Моя сеть"
time.sleep(5)
my_network_tab = driver.find_element(By.XPATH, "//a[contains(@href, '/mynetwork/')]")
my_network_tab.click()

# Переход на вкладку "Connections"
time.sleep(5)
connections_tab = driver.find_element(By.XPATH, "//a[@href='/mynetwork/invite-connect/connections/']")
connections_tab.click()

link_search = driver.find_element('xpath', '/html/body/div[5]/div[3]/div/div/div/div/div[2]/div/div/main/div/section/div[1]/div[2]/a')
link_search.click()
time.sleep(3)

# Установка фильтра по стране - РФ
time.sleep(3)
country_filter_items = driver.find_elements(By.XPATH, '//input[@name="locations-filter-value"]')

for item in country_filter_items:
    if item.get_attribute("value") == "101728296":
        item.click()
        break

# Установка фильтра по языкам - Русский и Английский
time.sleep(3)
language_filter_items = driver.find_elements(By.XPATH, '//input[@name="profile-language-filter-value"]')

for item in language_filter_items:
    language = item.get_attribute("value")
    if language == "ru" or language == "en":
        item.click()

# Нажатие на кнопку "Show results"
time.sleep(3)
show_results_button = driver.find_element(By.XPATH, '//button[contains(@class, "search-reusables__secondary-filters-show-results-button")]')
show_results_button.click()

# Получение списка контактов и вывод почты каждого человека на новой строке
time.sleep(3)
contacts = driver.find_elements(By.XPATH, "//li[@class='mn-connection-card__card ember-view']")

for contact in contacts:
    email = contact.find_element(By.XPATH, ".//a[contains(@href, 'mailto:')]").get_attribute("href")[7:]
    print(email)

# Закрытие браузера
driver.quit()
