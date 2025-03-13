from fastapi import FastAPI, Request
import uvicorn, requests, json, time, jwt
from db import *
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from config import STOCKAPI_KEY, SECRET_KEY, ALGORITHM
from bs4 import BeautifulSoup

app = FastAPI()
url = "http://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"
v1api = "/api/v1"
ERM = "error"

def get_stock_price(stock_code):
    url = f"https://finance.naver.com/item/main.nhn?code={stock_code}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    price = soup.select_one(".no_today .blind").text
    intpirice = int(price.replace(",", ""))
    return intpirice

# realtime price
def search_stock(name, page, numofRows):
    params = {
        "serviceKey": STOCKAPI_KEY,
        "resultType": "json",
        "likeItmsNm" : name,
        "pageNo" : page,
        "numOfRows" : numofRows
    }
    stock_requests = requests.get(url, params=params)
    stock_json = stock_requests.json()["response"]["body"]["items"]["item"]
    for i in range(len(stock_json)):
        stock_json[i]["realtime"] = get_stock_price(stock_json[i]["srtnCd"])
    total_count = int(stock_requests.json()["response"]["body"]["totalCount"])
    pages = total_count // numofRows
    if total_count % numofRows != 0:
        pages += 1
    return {"stocks" : stock_json, "pages" : pages}

def check_stock(stock_name):
    params = {
        "serviceKey": STOCKAPI_KEY,
        "numOfRows": 1,
        "resultType": "json",
        "itmsNm": stock_name
    }
    stock_requests = requests.get(url, params=params)
    stock_json = stock_requests.json()["response"]["body"]["items"]["item"]
    if len(stock_json) == 0:
        return False
    else:
        stock_json[0]["realtime"] = get_stock_price(stock_json[0]["srtnCd"])
        return stock_json

def create_jwt(userid, days):
    data = {
        "userid": userid,
        "exp": (datetime.now() + timedelta(days=days)).strftime("%Y%m%d%H%M%S")
    }
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def check_jwt(jwt_token):
    try:
        decoded_jwt = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        dt_object = datetime.strptime(decoded_jwt['exp'], "%Y%m%d%H%M%S")
        if dt_object < datetime.now():
            return "TokenExpired"
        else:
            if check_user(decoded_jwt["userid"]) == False:
                return "InvalidUser"
            else:
                return True
    except:
        return "InvalidToken"

def decode_jwt(jwt_token):
    try:
        decoded_jwt = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_jwt
    except:
        return "InvalidToken"

@app.get("/ip")
async def get_ip(request: Request):
    client_ip = request.client.host
    return {"ip": client_ip}

@app.get(f"{v1api}/login")
async def login(request: Request):
    return create_jwt("admin", 1)

class StockGet(BaseModel):
    page: int = None
    numofrows: int = None
    jwt: str

@app.post(f"{v1api}/get_stocks")
async def get_stocks(stock: StockGet):
    start_t = time.time()
    jwt_token = stock.jwt
    page = stock.page
    numofrows = stock.numofrows
    jwt_check = check_jwt(jwt_token)
    if jwt_check != True:
        return {"message": jwt_check}
    if page == None:
        page = 1
    if numofrows == None:
        numofrows = 10
    params = {
        "serviceKey": STOCKAPI_KEY,
        "pageNo": page,
        "numOfRows": numofrows,
        "resultType": "json"
    }
    stock_requests = requests.get(url, params=params)
    stock_json = stock_requests.json()["response"]["body"]["items"]["item"]
    total_count = int(stock_requests.json()["response"]["body"]["totalCount"])
    pages = total_count // numofrows
    if total_count % numofrows != 0:
        pages += 1
    message = "Success"
    if len(stock_json) == 0:
        message = "NoData"
    end_t = time.time()
    times = end_t - start_t
    return {
        "pages": pages,
        "message": message,
        "stocks": stock_json,
        "request_time": times
    }

class StockBuy(BaseModel):
    jwt: str
    stock_name: str
    stock_count: int

@app.post(f"{v1api}/buy_stock")
async def buy_stock(request: StockBuy):
    check_jwts = check_jwt(request.jwt)
    if check_jwts != True:
        return {"message": check_jwts}
    else:
        check_jwts = decode_jwt(request.jwt)
        check_stock_name = check_stock(request.stock_name)
        if check_stock_name == False:
            return {"message": "InvalidStock"}
        userid = check_jwts["userid"]
        stock_name = request.stock_name
        stock_count = request.stock_count
        stockmoney = stock_count * int(check_stock_name[0]["realtime"])
        chmoney = check_money(userid, stockmoney)
        if chmoney == ERM:
            return {"message": "DBError"}
        if chmoney == False:
            user = get_user(userid)
            require_money = stockmoney - user[3] 
            return {
                "message": "NotEnoughMoney",
                "require_money": require_money
            }
        else:
            addmoney = add_money(userid, -stockmoney)
            if addmoney == ERM:
                return {"message": "DBError"}
            adstock = add_stock(userid, stock_name, stock_count)
            if adstock == ERM:
                return {"message": "DBError"}
            else:
                return {"message": "Success"}

class Search(BaseModel):
    jwt: str
    include: str
    page: int = None
    numofrows: int = None

@app.get(f"{v1api}/search_stock")
async def searchstock(request: Search):
    try:
        chjwt = check_jwt(request.jwt)
        if chjwt != True:
            return {"message": chjwt}
        stocks = search_stock(request.include, request.page, request.numofrows)
        return {"stocks": stocks}
    except:
        return {"message": "APIError"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1010)