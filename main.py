from fastapi import FastAPI, Response, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from datetime import date
import datetime
import hashlib
from hashlib import sha256
from fastapi import Depends, FastAPI, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import FastAPI, Response, Cookie, HTTPException


app = FastAPI()
security = HTTPBasic()
app.secret_key = 'dsadsafdsnfdsjkn321ndsalndsa'
app.counter = 1
app.session_token = ''

class Patient(BaseModel):
    id: Optional[int] = None
    name: str
    surname: str
db = []

@app.get("/",status_code = status.HTTP_200_OK)
def root():
    return {"message": "Hello world!"}

@app.get("/method",status_code = status.HTTP_200_OK)
def root():
    return {"method": "GET"}

@app.post("/method",status_code=status.HTTP_201_CREATED)
def root():
    return {"method": "POST"}

@app.delete("/method",status_code = status.HTTP_200_OK)
def root():
    return {"method": "DELETE"}

@app.put("/method",status_code = status.HTTP_200_OK)
def root():
    return {"method": "PUT"}

@app.options("/method",status_code = status.HTTP_200_OK)
def root():
    return {"method": "OPTIONS"}




@app.get("/auth",status_code = status.HTTP_204_NO_CONTENT)
def check(response: Response,password: str='', password_hash: str=''):
    h = hashlib.sha512( str( password ).encode("utf-8") ).hexdigest()
    if(password ==''):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return 401
    if(h.strip() == password_hash.strip()):
        response.status_code = status.HTTP_204_NO_CONTENT
        return 204
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return 401





@app.post("/register",status_code=status.HTTP_201_CREATED)
def create_patient(patient: Patient):
    patient_dict = patient.dict()
    add_days = 0
    for char in range(0,len(patient.name)):
        if(patient.name[char].isalpha()==True):
            add_days = add_days + 1
    for char in range(0,len(patient.surname)):
        if(patient.surname[char].isalpha()==True):
            add_days = add_days + 1
    patient_dict.update({"id": len(db)+1,
    "register_date": datetime.date.today(),
     "vaccination_date":datetime.date.today()+datetime.timedelta(days=+add_days) })

    db.append(patient_dict)
    return db[-1]

@app.get("/patient/{id}",status_code = status.HTTP_200_OK)
def get_patient(id: int,response: Response):
    if(id<1):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return 400
    if id >len(db):
        response.status_code = status.HTTP_404_NOT_FOUND
        return 404
    
    return db[id-1]

@app.get("/hello",response_class=HTMLResponse)
def root():
    today = date.today()
    # d1 = today.strftime("%d-%m-%Y")
    d1 = today.strftime("%Y-%m-%d")


    return f"""
    <html>
        <head>
            <title>content-type</title>
        </head>
        <body>
            <h1>Hello! Today date is {d1}</h1>
        </body>
    </html>
    """.format(d1)


@app.post("/login_session",status_code = status.HTTP_201_CREATED)
def login_session( response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    if(username == "4dm1n" and password == "NotSoSecurePa$$"):
        session_token = sha256(f"{username}{password}{app.secret_key}".encode()).hexdigest() +str(app.counter)
        app.session_token = session_token
        response.set_cookie(key="session_token", value=session_token)
        app.counter = app.counter +1

    else:    
        response.status_code = 401
        return response


@app.post("/login_token",status_code = status.HTTP_201_CREATED)
def login_token( response: Response, session_token: str = Cookie(None),credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    session_token = sha256(f"{username}{password}{app.secret_key}".encode()).hexdigest()
    if(username == "4dm1n" and password == "NotSoSecurePa$$"):
        session_token = sha256(f"{username}{password}{app.secret_key}".encode()).hexdigest() +str(app.counter)
        app.session_token = session_token
        response.set_cookie(key="session_token", value=session_token)
        app.counter = app.counter +1
        return { "token":app.session_token}
    elif session_token == session_token:
        return { "token":app.session_token}

    else:
        response.status_code = 401
        return response
