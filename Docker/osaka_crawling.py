import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

import re
import pandas as pd
import datetime
import os

def crawling_naver(url):
    options = Options()
    options.add_argument("--headless")  # 헤드리스 모드 활성화
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--window-size=1920x1080')
    
    now = datetime.datetime.now()    
    formatted_now = now.strftime("%Y-%m-%d %H:%M")

    URL = url
    browser = webdriver.Chrome(options=options)
    browser.get(URL)
    time.sleep(1)
    browser.maximize_window()

    # 오사카 고르기

    browser.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[4]/div/div/div[2]/div[1]/button[2]').click()
    browser.implicitly_wait(1)

    browser.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[10]/div[2]/section/section/button[2]').click()
    browser.implicitly_wait(1)

    browser.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[10]/div[2]/section/section/div/button[1]').click()
    browser.implicitly_wait(1)

    # 날짜 고르기

    # 가는 날 버튼 -> 캘린더 열기
    browser.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[4]/div/div/div[2]/div[2]/button[1]').click()
    browser.implicitly_wait(3)

    # 가는 날 선택
    browser.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[10]/div[2]/div[1]/div[2]/div/div[2]/table/tbody/tr[4]/td[6]/button').click()
    time.sleep(2)

    # 오는 날 선택
    browser.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[10]/div[2]/div[1]/div[2]/div/div[2]/table/tbody/tr[4]/td[7]/button').click()
    browser.implicitly_wait(3)

    # 직항 선택
    browser.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[4]/div/div/div[2]/div[3]/button[2]').click()
    browser.implicitly_wait(3)

    # 항공권 검색
    browser.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[4]/div/div/div[2]/button').click()
    browser.implicitly_wait(20)

    # 편도 검색
    browser.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/div[3]/div/div[1]/div/div/div[1]/button[2]').click()
    browser.implicitly_wait(5)

    browser.find_element(By.XPATH,'//*[@id="__next"]/div/div[1]/div[3]/div/div[1]/div/div/div[2]/button/span').click()
    browser.implicitly_wait(20)

    # 카드 혜택 제외하기
    browser.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/div[7]/div/div[1]/div/div[2]/button').click()
    browser.implicitly_wait(3)
    browser.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/div[7]/div/div[1]/div/div[2]/div/button[2]/span').click()
    browser.implicitly_wait(3)

    # 긁어 오기

    airline = [] # 항공사 이름
    take_off = [] # 이륙 시간
    landing = [] # 착륙 시간
    take_off_airport = [] # 출발 공항
    landing_airport = [] # 도착 공항
    non_stop_transit = [] # 직항 or 경유
    ftime = [] # 항공시간
    one_way_round = [] # 편도 or 왕복
    ticket_price = [] # 티켓 가격

    html=browser.page_source
    soup=BeautifulSoup(html,'html.parser')


    # 항공사 이름
    air_names=soup.select('b.airline_name__Tm2wJ')
    # 이륙 시간, 착륙 시간
    flights_check=soup.select('b.route_time__-2Z1T')
    # 출발 공항, 도착 공항
    flights_place=soup.select('i.route_code__3WUFO')
    # 직항, 걸리는 시간
    flights_times = soup.select('i.route_info__1RhUH')
    # 편도, 가격
    money = soup.select('b.item_usual__dZqAN')


    for i in range(len(air_names)):
        airline.append(air_names[i].get_text())
        time.sleep(0.1)


    for i in range(len(flights_check)):
        if i % 2 == 0:
            take_off.append(flights_check[i].get_text())
        else : 
            landing.append(flights_check[i].get_text())    
        time.sleep(0.1)


    for i in range(len(flights_place)):
        if i % 2 == 0:
            take_off_airport.append(flights_place[i].get_text())
        else : 
            landing_airport.append(flights_place[i].get_text())
        time.sleep(0.1)


    for i in range(len(flights_times)):
        way_n_time = re.split(', ', flights_times[i].get_text())
        non_stop_transit.append(way_n_time[0])
        ftime.append(way_n_time[1])
        time.sleep(0.1)


    for i in range(len(money)):
        money_info = re.split(' ', money[i].get_text())
        one_way_round.append(money_info[0])
        ticket_price.append(money_info[1][:-1])
        time.sleep(0.1)


    data = { "항공사" : airline,
            "이륙 시간" : take_off,
            "출발 공항" : take_off_airport,
            "착륙 시간" : landing,
            "도착 공항" : landing_airport,
            "직항, 경유" : non_stop_transit,
            "항공 시간" : ftime,
            "편도, 왕복" : one_way_round,
            "티켓 가격" : ticket_price,
            "크롤링 시작" : formatted_now
            }

    time.sleep(1)

    browser.close()

    return data


def main():

    url = "https://flight.naver.com"

    df = pd.DataFrame(crawling_naver(url))


    if not os.path.exists("/app/data/"):
        df.to_csv("/app/data/naver.csv", index=False, mode = "w", encoding="utf-8")
    else :
        df.to_csv("/app/data/naver.csv", index=False, mode = "a", encoding="utf-8", header=False)

if __name__ == "__main__":
    main()