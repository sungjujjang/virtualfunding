from fastapi import FastAPI, Request
import uvicorn, requests, json, time, jwt
from db import *
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from config import STOCKAPI_KEY, SECRET_KEY, ALGORITHM
from bs4 import BeautifulSoup
# add cors
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
url = "http://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"
v1api = "/api/v1"
ERM = "error"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서의 요청 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

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

def check_stock_7(stock_name):
    params = {
        "serviceKey": STOCKAPI_KEY,
        "numOfRows": 7,
        "resultType": "json",
        "itmsNm": stock_name
    }
    stock_requests = requests.get(url, params=params)
    stock_json = stock_requests.json()["response"]["body"]["items"]["item"]
    if len(stock_json) == 0:
        return False
    else:
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
            
class StockSell(BaseModel):
    jwt: str
    stock_name: str
    stock_count: int
    
@app.post(f"{v1api}/sell_stock")
async def sell_stock(request: StockSell):
    check_jwts = check_jwt(request.jwt)
    if check_jwts != True:
        return {"message": check_jwts}
    else:
        check_jwts = decode_jwt(request.jwt)
        userid = check_jwts["userid"]
        check_stock_userone = check_stock_user(userid, request.stock_name)
        check_stock_zero(userid)
        if check_stock_userone == False:
            return {"message": "InvalidStock"}
        stock_name = request.stock_name
        stock_count = request.stock_count
        if check_stock_userone[2] < stock_count:
            return {"message": "NotEnoughStock"}
        stock_mon = check_stock(request.stock_name)[0]["realtime"]
        if stock_mon == False:
            return {"message": "InvalidStock"}
        stockmoney = stock_count * int(stock_mon)
        if check_stock_userone == ERM:
            return {"message": "DBError"}
        addmoney = add_money(userid, stockmoney)
        if addmoney == ERM:
            return {"message": "DBError"}
        adstock = add_stock(userid, stock_name, -stock_count)
        if adstock == ERM:
            return {"message": "DBError"}
        else:
            check_stock_zero(userid)
            return {"message": "Success"}

class Search(BaseModel):
    jwt: str
    include: str
    page: int = None
    numofrows: int = None

@app.post(f"{v1api}/search_stock")
async def searchstock(request: Search):
    try:
        chjwt = check_jwt(request.jwt)
        if chjwt != True:
            return {"message": chjwt}
        stocks = search_stock(request.include, request.page, request.numofrows)
        return {"stocks": stocks}
    except:
        return {"message": "APIError"}
    
class Register(BaseModel):
    id: str
    password: str
    name: str
    email: str = None

@app.post(f"{v1api}/register")
async def register(request: Register):
    id = request.id
    password = request.password
    name = request.name
    email = request.email
    check_userstr = check_id_string(id)
    check_passwordstr = check_password_string(password)
    if check_userstr == False:
        return {"message": "아이디는 4자 이상 20자 이하의 영문자, 숫자, _ 만 가능합니다."}
    if check_passwordstr == False:
        return {"message": "비밀번호는 8자 이상 20자 이하의 영문자, 숫자, 특수문자만 가능합니다."}
    user = check_user(id)
    if user == ERM:
        return {"message": "DBError"}
    if user == True:
        return {"message": "AlreadyExists"}
    password = hash_password(password)
    adduser = add_user(id, name, password, email=email)
    if adduser == ERM:
        return {"message": "DBError"}
    else:
        jwt = create_jwt(id, 1)
        return {"message": "Success", "jwt": jwt}
    
class Login(BaseModel):
    id: str
    password: str
    login_days: int = 1

@app.post(f"{v1api}/login")
async def login(request: Login):
    id = request.id
    password = request.password
    login_days = request.login_days
    user = check_user(id)
    if user == ERM:
        return {"message": "DBError"}
    if user == False:
        return {"message": "InvalidUser"}
    checkpass = check_password(id, password)
    if checkpass == ERM:
        return {"message": "DBError"}
    if checkpass == False:
        return {"message": "InvalidPassword"}
    jwt = create_jwt(id, login_days)
    return {"message": "Success", "jwt": jwt}

class Checkid(BaseModel):
    id: str
    
@app.post(f"{v1api}/check_id")
async def checkid(request: Checkid):
    checkuser = check_user(request.id)
    if checkuser == ERM:
        return {"message": "DBError"}
    if checkuser == True:
        return {"message": "AlreadyExists"}
    else:
        return {"message": "Available"}
    
class Get7days(BaseModel):
    jwt: str
    stock_name: str
    
@app.post(f"{v1api}/get_7days")
async def get7days(request: Get7days):
    checkjwt = check_jwt(request.jwt)
    if checkjwt != True:
        return {"message": checkjwt}
    stock_name = request.stock_name
    stocks = check_stock_7(stock_name)
    if stocks == False:
        return {"message": "InvalidStock"}
    return stocks

class DeleteUser(BaseModel):
    jwt: str
    password: str

@app.delete(f"{v1api}/delete_user")
async def delete_user_(request: DeleteUser):
    checkjwt = check_jwt(request.jwt)
    if checkjwt != True:
        return {"message": checkjwt}
    checkjwt = decode_jwt(request.jwt)
    userid = checkjwt["userid"]
    checkpass = check_password(userid, request.password)
    if checkpass == ERM:
        return {"message": "DBError"}
    if checkpass == False:
        return {"message": "InvalidPassword"}
    deluser = delete_user(userid)
    if deluser == ERM:
        return {"message": "DBError"}
    return {"message": "Success"}

class ChangePassword(BaseModel):
    jwt: str
    password: str
    new_password: str

@app.put(f"{v1api}/change_password")
async def change_password(request: ChangePassword):
    checkjwt = check_jwt(request.jwt)
    if checkjwt != True:
        return {"message": checkjwt}
    checkjwt = decode_jwt(request.jwt)
    userid = checkjwt["userid"]
    checkpass = check_password(userid, request.password)
    if checkpass == ERM:
        return {"message": "DBError"}
    if checkpass == False:
        return {"message": "InvalidPassword"}
    new_password = request.new_password
    check_passwordstr = check_password_string(new_password)
    if check_passwordstr == False:
        return {"message": "비밀번호는 8자 이상 20자 이하의 영문자, 숫자, 특수문자만 가능합니다."}
    new_password = hash_password(new_password)
    changepass = change_passwords(userid, new_password)
    if changepass == ERM:
        return {"message": "DBError"}
    return {"message": "Success"}

class ChangeEmail(BaseModel):
    jwt: str
    email: str

@app.put(f"{v1api}/change_email")
async def change_email(request: ChangeEmail):
    checkjwt = check_jwt(request.jwt)
    if checkjwt != True:
        return {"message": checkjwt}
    checkjwt = decode_jwt(request.jwt)
    userid = checkjwt["userid"]
    changeemail = change_emails(userid, request.email)
    if changeemail == ERM:
        return {"message": "DBError"}
    return {"message": "Success"}

class Changenickname(BaseModel):
    jwt: str
    nickname: str

@app.put(f"{v1api}/change_nickname")
async def change_nickname(request: Changenickname):
    checkjwt = check_jwt(request.jwt)
    if checkjwt != True:
        return {"message": checkjwt}
    checkjwt = decode_jwt(request.jwt)
    userid = checkjwt["userid"]
    changenickname = change_nicknames(userid, request.nickname)
    if changenickname == ERM:
        return {"message": "DBError"}
    return {"message": "Success"}

class Getuser(BaseModel):
    jwt: str
    
@app.post(f"{v1api}/get_user")
async def get_user_(request: Getuser):
    checkjwt = check_jwt(request.jwt)
    if checkjwt != True:
        return {"message": checkjwt}
    checkjwt = decode_jwt(request.jwt)
    userid = checkjwt["userid"]
    user = get_user(userid)
    if user == ERM:
        return {"message": "DBError"}
    listuser = list(user)
    del listuser[4]
    del listuser[4]
    return {"message": "Success", "user": listuser}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1010)