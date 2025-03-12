from fastapi import FastAPI, Request
import uvicorn, requests, json, time, jwt
from db import *
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from config import STOCKAPI_KEY, SECRET_KEY, ALGORITHM

app = FastAPI()
url = "http://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"

def create_jwt(userid, days):
    data = {
        "userid": userid,
        "exp": (datetime.now() + timedelta(days=days)).strftime("%Y%m%d%H%M%S")
    }
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/ip")
async def get_ip(request: Request):
    client_ip = request.client.host
    return {"ip": client_ip}

@app.get("/login")
async def login(request: Request):
    return create_jwt("test", 1)

@app.post("/get_stocks")
async def get_stocks(request: Request):
    start_t = time.time()
    json = await request.json()
    page = json["page"]
    numofrows = json["numofrows"]
    jwt_token = json["jwt"]
    try:
        decoded_jwt = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        dt_object = datetime.strptime(decoded_jwt['exp'], "%Y%m%d%H%M%S")
        if dt_object < datetime.now():
            return {"message": "ExpiredJWT"}
        else:
            pass
    except:
        return {"message": "InvalidJWT"}
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
    message = "Success"
    if len(stock_json) == 0:
        message = "NoData"
    end_t = time.time()
    times = end_t - start_t
    return {
        "message": message,
        "stocks": stock_json,
        "request_time": times
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1010)