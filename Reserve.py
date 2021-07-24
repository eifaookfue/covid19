from os import system
from time import sleep

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

chrome_path = r'C:\Apl\chromedriver\chromedriver'

options = Options()
options.add_argument('--incognito')

driver = webdriver.Chrome(executable_path=chrome_path, options=options)

url = 'https://v-yoyaku.jp/131237-edogawa'
driver.get(url)

#driver.implicitly_wait(10)

#sleep(3)

loginId = '5000580118'
pwd = '19750815'
login_box = driver.find_element_by_id('login_id')
pwd_box = driver.find_element_by_id('login_pwd')

login_button = driver.find_element_by_id('btn_login')
login_box.send_keys(loginId)
pwd_box.send_keys(pwd)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
sleep(3)
login_button.click()

# 予約・変更するボタン
preserve_button = WebDriverWait(driver, 10).until(
    expected_conditions.visibility_of_element_located(
        (
            By.ID, 'mypage_accept'
        )
    )
)
preserve_button.click()

# 接種会場を選択ボタン
#site_button = driver.find_element_by_id('btn_Search_Medical')
site_button = WebDriverWait(driver, 10).until(
    expected_conditions.visibility_of_element_located(
        (
            By.ID, 'btn_Search_Medical'
        )
    )
)
site_button.click()

# 検索ボタン
search_button = WebDriverWait(driver, 10).until(
    expected_conditions.visibility_of_element_located(
        (
            By.CSS_SELECTOR, 'button#btn_search_medical[type="button"]'
        )
    )
)
search_button.click()
sleep(5)
#driver.find_element_by_tag_name('table')
#table_element = driver.find_element_by_css_selector('table#search-medical-table')
soup = BeautifulSoup(driver.page_source, 'html.parser')
table = soup.select_one('table#search-medical-table')
list = [e.getText() for e in table.select_one('tbody').select('tr')]
print(list)

if list[0] == '予約できる接種会場はありません。':
    print('Not found.')
    driver.quit()

radio = driver.find_element_by_xpath('//*[@id="search-medical-table"]/tbody[1]/tr/td[1]')
radio.click()
sleep(10)
#table_element.

# --> STEP3 : スクロールして表示件数を増やす
# height = 500
# while height < 3000:

#     driver.execute_script("window.scrollTo(0, {});".format(height))
#     height += 100
#     print(height)

#     sleep(1)

driver.quit()
