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
import secrets
from fastapi.responses import PlainTextResponse, RedirectResponse
import random
import sqlite3


app = FastAPI()
security = HTTPBasic()
app.secret_key = 'dsadsafdsnfdsjkn321ndsalndsa'
app.counter = 1
app.access_sessions = []
app.access_tokens = []


class Patient(BaseModel):
    id: Optional[int] = None
    name: str
    surname: str
db = []


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()





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
    username = secrets.compare_digest(credentials.username, "4dm1n")
    password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")
    if not (username and password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED)
    rand = str(random.randint(0,500000))
    session_token = sha256(f"{username}{password}{app.secret_key}{rand}".encode()).hexdigest()
    response.set_cookie(key="session_token", value=session_token)
    if len(app.access_sessions) >= 3:
        app.access_sessions.pop(0)
    app.access_sessions.append(session_token)



@app.post("/login_token",status_code = status.HTTP_201_CREATED)
def login_token( response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    username = secrets.compare_digest(credentials.username, "4dm1n")
    password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")
    if not (username and password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED)
    rand = str(random.randint(0,500000))
    session_token = sha256(f"{username}{password}{app.secret_key}{rand}".encode()).hexdigest()
    if len(app.access_tokens) >= 3:
        app.access_tokens.pop(0)
    app.access_tokens.append(session_token)
    

    return {"token": session_token}


@app.get("/welcome_session")
def welcome_session(format:str = "", session_token: str = Cookie(None), status_code = status.HTTP_200_OK):
    if session_token not in app.access_sessions or session_token == '':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED)
    if format == 'json':
        return {"message": "Welcome!"}
    elif format == 'html':
        return HTMLResponse(content = '<h1>Welcome!</h1>')
    else:
        return PlainTextResponse(content = 'Welcome!')

@app.get("/welcome_token")
def welcome_session(format:str = "", token: str = "", status_code = status.HTTP_200_OK):
    if token not in app.access_tokens or token == '':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED)
    if format == 'json':
        return {"message": "Welcome!"}
    elif format == 'html':
        return HTMLResponse(content = '<h1>Welcome!</h1>')
    else:
        return PlainTextResponse(content = 'Welcome!')


@app.delete('/logout_session')
def logout_session(format:str = "", session_token: str = Cookie(None)):
    if session_token not in app.access_sessions or session_token == '':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED)
    app.access_sessions.remove(session_token)
    response = RedirectResponse( url = '/logged_out?format=' + format, status_code = 302)
    return response

@app.delete('/logout_token')
def logout_session(format:str = "", token: str = ""):
    if token not in app.access_tokens or token == '':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED)
    app.access_tokens.remove(token)
    response = RedirectResponse( url ='/logged_out?format=' + format, status_code = 302)
    return response


@app.get('/logged_out', status_code = status.HTTP_200_OK)
def logged_out(format: str = ""):
    if format == 'json':
        return {"message": "Logged out!"}
    elif format == 'html':
        return HTMLResponse(content = '<h1>Logged out!</h1>')
    else:
        return PlainTextResponse(content = 'Logged out!')


@app.get("/categories", status_code = status.HTTP_200_OK)
async def categories():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute('SELECT CategoryID id , CategoryName name FROM Categories ORDER BY CategoryID').fetchall()
    return { "categories": data}

@app.get("/customers",status_code = status.HTTP_200_OK)
async def customers():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute('''
    SELECT CustomerID id, CompanyName name , COALESCE(Address, '') || ' ' || COALESCE(PostalCode, '')|| ' ' || COALESCE(City,'') || ' ' || COALESCE(Country,'') AS full_address FROM Customers ORDER BY UPPER(CustomerID)
    ''').fetchall()
    return { "customers": data}

@app.get('/products/{id}', status_code=status.HTTP_200_OK)
async def products(id: int):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(f'''SELECT ProductID id, ProductName name FROM Products WHERE id = {id}''' ).fetchone()
    if data == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return data

@app.get('/employees', status_code=status.HTTP_200_OK)
async def employees(limit: int = -1, offset: int = 0, order: str = 'id'):
    names = {'first_name' : 'FirstName',
     'last_name' : 'LastName', 
     'city' : 'City', 
     'id' : 'EmployeeID'}
    app.db_connection.row_factory = sqlite3.Row
    if order not in names.keys():
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST)
    data = app.db_connection.execute(f'SELECT EmployeeID id, LastName last_name, FirstName first_name,\
        City city FROM Employees ORDER BY {order} LIMIT {limit} OFFSET {offset}'
        ).fetchall()
    return {'employees' : data} 
