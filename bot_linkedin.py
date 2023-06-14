from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Введите свои учетные данные для входа в LinkedIn
username = 'nikitaserbije@gmail.com'
password = 'RolfGavno'

# Задайте свой запрос для поиска кандидатов
search_query = 'software engineer'

# Инициализируйте драйвер браузера
driver = webdriver.Chrome('/path/to/chromedriver')

# Зайдите на сайт LinkedIn и войдите в свой аккаунт
driver.get('https://www.linkedin.com/')
#login_link = driver.find_element_by_link_text('Sign in')
#login_link.click()
username_field = driver.find_element_by_id('username')
username_field.send_keys(username)
password_field = driver.find_element_by_id('password')
password_field.send_keys(password)
password_field.submit()

# Выполните поиск кандидатов по запросу
search_field = driver.find_element_by_xpath('//input[@aria-label="Search"]')
search_field.send_keys(search_query)
search_field.send_keys(Keys.ENTER)

# Дождитесь, пока страница с результатами поиска полностью загрузится
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//ul[@class="search-results__list"]'))
)

# Получите список профилей кандидатов
profiles = driver.find_elements_by_xpath('//ul[@class="search-results__list"]/li')

# Выведите имена кандидатов в консоль
for profile in profiles:
    name = profile.find_element_by_xpath('.//h3').text
    print(name)

# Закройте браузер
driver.quit()