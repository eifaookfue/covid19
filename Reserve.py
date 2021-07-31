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
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def notify(text):
    webhook_url = 'https://hooks.slack.com/services/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'
    requests.post(webhook_url, data = json.dumps({
        "text": text
    }))


def check(driver, text):
    WebDriverWait(driver, 10).until(
        expected_conditions.visibility_of_element_located(
            (
                By.CSS_SELECTOR, '.fc-day-top.fc-future'
            )
        )
    )
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    dict = {e['data-date']: e.select_one('.status-text').get_text() for e in soup.select('.fc-day-top.fc-future') if e.select_one('.status-text') is not None}
    logging.info(f"{text}={dict}")
    circle_date = [k for k, v in dict.items() if v == '○']
    if len(circle_date) > 0:
        notify(f'Circle: {",".join(circle_date)}')
    triangle_date = [k for k, v in dict.items() if v == '△']
    if len(triangle_date) > 0:
        notify(f'Triangle: {",".join(triangle_date)}')


def execute(searched_roomd_list):

    chrome_path = r'C:\Apl\chromedriver\chromedriver'

    options = Options()
    options.add_argument('--incognito')

    driver = webdriver.Chrome(executable_path=chrome_path, options=options)

    url = 'https://v-yoyaku.jp/131237-edogawa'
    driver.get(url)

    # 私は優先接種対象者に該当します。
    prio_radio_button = WebDriverWait(driver, 10).until(
        expected_conditions.visibility_of_element_located(
            (
                By.NAME, 'prio_tgt'
            )
        )
    )
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    prio_radio_button.click()

    loginId = '5000580118'
    pwd = '19750815'
    login_box = driver.find_element_by_id('login_id')
    pwd_box = driver.find_element_by_id('login_pwd')

    login_button = driver.find_element_by_id('btn_login')
    login_box.send_keys(loginId)
    pwd_box.send_keys(pwd)
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
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
        WebDriverWait(driver, 20).until(
            expected_conditions.visibility_of_any_elements_located(
                (
                    By.CSS_SELECTOR, 'table#search-medical-table > tbody[style="word-break: break-all"] > tr'
                )
            )
        )
        #sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.select_one('table#search-medical-table')
        if table.select_one('tbody[style="word-break: break-all"] > tr').getText() == '予約できる接種会場はありません。':
            logging.info('Sleep 60 seconds because of no open rooms.')
            sleep(60)
        else:
            dict = {e.select_one('td:nth-of-type(1) > span > input').get('id'): e.select_one('td:nth-of-type(2)').getText() 
                for e in table.select_one('tbody[style="word-break: break-all"]').select('tr')}
            logging.info(dict)
            searched_key = next(iter(dict.keys()))
            logging.info(f"serched_key={searched_key}")
            break


    # 会場が一つしか見つからなかったら仕方ないのでもう一度同じ会場で実行
    if len(dict) != 1:
        dict = {k: v for k, v in dict.items() if v not in searched_roomd_list}
        # すべて探索し終わったら仕方ないので先頭の会場でもう一度実行
        if len(dict) > 0:
            searched_key = next(iter(dict.keys()))
            logging.info(f"serched_key={searched_key}")

    searched_room = dict[searched_key]
    logging.info(f"serched_room={searched_room}")
    radio = driver.find_element_by_id(searched_key)
    radio.click()

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # この接種会場を予約ボタン
    reserve_button = driver.find_element_by_id('btn_select_medical')
    reserve_button.click()

    check(driver, "First Month")

    # 次へボタン 8月
    next_button = WebDriverWait(driver, 10).until(
        expected_conditions.element_to_be_clickable(
            (
                By.CSS_SELECTOR, '.fc-next-button'
            )
        )
    )
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    next_button.click()
    check(driver, "Second Month")

    # 次へボタン 9月
    next_button = WebDriverWait(driver, 10).until(
        expected_conditions.element_to_be_clickable(
            (
                By.CSS_SELECTOR, '.fc-next-button'
            )
        )
    )
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    next_button.click()
    check(driver, "Third Month")

    driver.quit()

    return searched_room

searched_rooms = []
while True:
    searched_rooms.append(execute(searched_rooms))
    logging.info("Sleep another 60 seconds.")
    sleep(60)    


