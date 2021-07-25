from os import system
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import json

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

while True:
    search_button.click()
    sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.select_one('table#search-medical-table')
    list = [e.getText() for e in table.select_one('tbody').select('tr')]
    if list[0] != '予約できる接種会場はありません。':
        break
    else:
        sleep(60)

print(list)
text = ",".join(list)
webhook_url = 'https://hooks.slack.com/services/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'
# requests.post(webhook_url, data = json.dumps({
#     "text": text
# }))

radio = driver.find_element_by_id('search_medical_table_radio_0')
radio.click()

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# この接種会場を予約ボタン
reserve_button = driver.find_element_by_id('btn_select_medical')
reserve_button.click()

sleep(5)

soup = BeautifulSoup(driver.page_source, 'html.parser')
dict = {e['data-date']: e.select_one('.status-text').get_text() for e in soup.select('.fc-day-top.fc-future') if e.select_one('.status-text') is not None}
print(dict)
dict = {k: v for k, v in dict.items() if v == '○' or v == '△' }
print(dict.values())

sleep(3)

# 次へボタン 8月
next_button = driver.find_element_by_css_selector('.fc-next-button')
next_button.click()
sleep(3)
soup = BeautifulSoup(driver.page_source, 'html.parser')
dict = {e['data-date']: e.select_one('.status-text').get_text() for e in soup.select('.fc-day-top.fc-future') if e.select_one('.status-text') is not None}
print(dict)
dict = {k: v for k, v in dict.items() if v == '○' or v == '△' }
print(dict.values())

# 次へボタン 9月
next_button = driver.find_element_by_css_selector('.fc-next-button')
next_button.click()
sleep(3)
soup = BeautifulSoup(driver.page_source, 'html.parser')
dict = {e['data-date']: e.select_one('.status-text').get_text() for e in soup.select('.fc-day-top.fc-future') if e.select_one('.status-text') is not None}
print(dict)
dict = {k: v for k, v in dict.items() if v == '○' or v == '△' }
print(dict.values())


#driver.quit()


