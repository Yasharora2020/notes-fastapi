from pydantic import BaseModel
from typing import Optional, List



class Note(BaseModel):
    title: str
    content: str


class NoteCreate(BaseModel):
    title: str
    content: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserInDB(UserCreate):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str 


class UserBase(BaseModel):
    username: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
