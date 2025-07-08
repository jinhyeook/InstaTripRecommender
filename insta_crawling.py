from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

import time
import re

def insta_searching(word): # 장소에 대한 게시물이 모여있는 곳으로 이동
    url="https://www.instagram.com/"+str(word)+"/"
    return url

def select_first(driver): # 첫 번째 게시물 선택
    first = driver.find_element(By.CSS_SELECTOR, "div._aagw")
    first.click()
    time.sleep(3)

def get_content(driver):
    
    html=driver.page_source
    soup=BeautifulSoup(html,'lxml')
    try:
        content = soup.select('div._a9zs')[0].text # 내용
    except:
        content=''
    
    tags=re.findall(r'#[^Ws#,WW]+',content)
    
    data = soup.select('time._aaqe')[0]['datetime'][:10] # 날짜
    
    try:
        like=soup.select('span.html-span.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1hl2dhg.x16tdsg8.x1vvkbs')[0].text # 좋아요 수
    except:
        like=0
    
    try:
        place = soup.select('div._aaqm')[0].text # 장소
    except:
        place=''
        
    try:   
        img_element = driver.find_element(By.CSS_SELECTOR,'._aatk .x5yr21d.xu96u03.x10l6tqk.x13vifvy.x87ps6o.xh8yej3') 
        img_src = img_element.get_attribute('src') # 이미지
    except:
        img_src=''
        
    data=[content,data,like,place,tags,img_src]
    
    return data

def move_next(driver): # 다음 게시물 이동
    right = driver.find_element(By.CSS_SELECTOR, "div._aaqg._aaqh")
    right.click()
    time.sleep(3)
    
#--------------------------------------------------------------------------------

from urllib.parse import quote_plus
from selenium.webdriver.common.by import By

# Chrome 웹 드라이버를 시작
driver = webdriver.Chrome()
driver.get('https://www.instagram.com')
time.sleep(3)

email = '아이디'
input_id = driver.find_element(By.NAME, 'username')
input_id.clear()
input_id.send_keys(email)

password = '비밀번호'
input_pw = driver.find_element(By.NAME, 'password')
input_pw.clear()
input_pw.send_keys(password)
input_pw.submit()

time.sleep(5)

word = input("검색어를 입력하세요: ")
url = insta_searching(word)

driver.get(url)
time.sleep(15)

select_first(driver)

results = []
target = 201 #크롤링할 게시물 수
for i in range(target):
    try:
        data = get_content(driver)
        results.append(data)
        move_next(driver)
    except:
        time.sleep(2)
        move_next(driver)

driver.close()