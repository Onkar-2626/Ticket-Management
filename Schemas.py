from pydantic import BaseModel, EmailStr
from typing import Optional

class customer(BaseModel):
    name: str
    email: EmailStr
    password: str      
    phone_no: str
    gender: str
    age: int


class booking(BaseModel):
    name: str
    source: str
    destination: str


class payment(BaseModel):
    bid: int
    name: str
    payment_status: str


# Login Schema
class Login(BaseModel):
    email: EmailStr
    password: str