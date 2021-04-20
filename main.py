from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from typing import Optional
import datetime
import hashlib


app = FastAPI()

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
    if(h.strip() == password_hash.strip()):
        response.status_code = status.HTTP_204_NO_CONTENT
        return 204
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return 401





@app.post("/register",status_code=status.HTTP_201_CREATED)
def create_patient(patient: Patient):
    patient_dict = patient.dict()
    add_days = len(patient.name) +len(patient.surname)
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