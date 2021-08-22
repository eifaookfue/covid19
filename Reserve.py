from os import system
from time import sleep
from pit import Pit
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
from retry import retry
import traceback
from datetime import datetime
import sys

file_handler = logging.FileHandler(filename="c:/logs/reserve.log")
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    handlers=handlers,
    datefmt='%Y-%m-%d %H:%M:%S')

def notify(text):
    webhook_url = Pit.get('slack-my-url')
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
        logging.info(f'Circle found. {",".join(circle_date)}')
        notify(f'Circle: {",".join(circle_date)}')
    triangle_date = [k for k, v in dict.items() if v == '△']
    if len(triangle_date) > 0:
        logging.info(f'Triangle found. {",".join(triangle_date)}')
        notify(f'Triangle: {",".join(triangle_date)}')

@retry(tries=3, delay=5)
def execute(driver, searched_roomd_list):


    url = 'https://v-yoyaku.jp/131237-edogawa'
    driver.get(url)

    # 私は優先接種対象者に該当します。
    # prio_radio_button = WebDriverWait(driver, 10).until(
    #     expected_conditions.element_to_be_clickable (
    #         (
    #             By.NAME, 'prio_tgt'
    #         )
    #     )
    # )
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(3)
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # sleep(1)
    # prio_radio_button.click()

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
            break


    # 会場が一つしか見つからなかったら仕方ないのでもう一度同じ会場で実行
    if len(dict) == 1:
        logging.info(f"serched_key={searched_key}")
        searched_room = dict[searched_key]
    else:
        remained_dict = {k: v for k, v in dict.items() if v not in searched_roomd_list}
        # すべて探索し終わったら仕方ないので先頭の会場でもう一度実行
        if len(remained_dict) > 0:
            searched_key = next(iter(remained_dict.keys()))
            logging.info(f"serched_key={searched_key}")
            searched_room = remained_dict[searched_key]    
        else:
            logging.info(f"serched_key={searched_key}")
            searched_room = dict[searched_key]    

    logging.info(f"serched_room={searched_room}")
    #radio = driver.find_element_by_id(searched_key)
    radio = WebDriverWait(driver, 10).until(
        expected_conditions.element_to_be_clickable (
            (
                By.ID, searched_key
            )
        )
    )
    radio.click()
    sleep(1)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # この接種会場を予約ボタン
    #reserve_button = driver.find_element_by_id('btn_select_medical')
    reserve_button = WebDriverWait(driver, 10).until(
        expected_conditions.element_to_be_clickable(
            (
                By.ID, 'btn_select_medical'
            )
        )
    )
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
    sleep(3)
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
    sleep(3)
    next_button.click()
    check(driver, "Third Month")


    return searched_room

if __name__ == '__main__':
    searched_rooms = []
    error_count = 0

    chrome_path = r'C:\Apl\chromedriver\chromedriver'

    options = Options()
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('window-size=1920x1080')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(executable_path=chrome_path, options=options)

    while True:
        try:
            searched_rooms.append(execute(driver, searched_rooms))
            logging.info("Sleep another 60 seconds.")
            sleep(60)    
        except:
            traceback.print_exc()
            driver.save_screenshot(f"C:/Apl/projects/covid19/screenshot/error_{datetime.today().strftime('%Y%m%d%H%M%S')}.png")
        
        driver.close()
        driver.quit()

            


