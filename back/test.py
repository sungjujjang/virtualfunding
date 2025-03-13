import requests
from bs4 import BeautifulSoup

def get_stock_price(stock_code):
    url = f"https://finance.naver.com/item/main.nhn?code={stock_code}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    price = soup.select_one(".no_today .blind").text
    return price

# 삼성전자 (005930) 실시간 가격 조회
print("삼성전자 현재가:", get_stock_price("005930"))
