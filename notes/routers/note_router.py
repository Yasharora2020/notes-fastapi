from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import database
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..auth import get_current_user


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# User registration endpoint
@router.post("/users/", response_model=schemas.UserCreate)
async def create_user(user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    query = models.users.insert().values(username=user.username, hashed_password=hashed_password)
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}


# User login endpoint
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Implement the logic for user login and token generation
    user = await auth.authenticate_user(form_data.username, form_data.password)
    #print(user.id)
    #print(user.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# CRUD operations for notes
@router.post("/notes/", response_model=schemas.Note)
async def create_note(note: schemas.NoteCreate, current_user: schemas.User = Depends(get_current_user)):
    query = models.notes.insert().values(title=note.title, content=note.content, user_id=current_user.id)
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}

@router.get("/notes/", response_model=List[schemas.Note])
async def read_notes(current_user: schemas.User = Depends(get_current_user)):
    query = models.notes.select().where(models.notes.c.user_id == current_user.id)
    return await database.fetch_all(query)

@router.get("/notes/{note_id}", response_model=schemas.Note)
async def read_note(note_id: int, current_user: schemas.User = Depends(get_current_user)):
    query = models.notes.select().where(models.notes.c.id == note_id, models.notes.c.user_id == current_user.id)
    note = await database.fetch_one(query)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/notes/{note_id}", response_model=schemas.Note)
async def update_note(note_id: int, note: schemas.NoteCreate, current_user: schemas.User = Depends(get_current_user)):
    select_query = models.notes.select().where(models.notes.c.id == note_id, models.notes.c.user_id == current_user.id)
    existing_note = await database.fetch_one(select_query)
    if existing_note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    update_query = models.notes.update().where(models.notes.c.id == note_id).values(title=note.title, content=note.content)
    await database.execute(update_query)
    return {**note.dict(), "id": note_id}

@router.delete("/notes/{note_id}")
async def delete_note(note_id: int, current_user: schemas.User = Depends(get_current_user)):
    delete_query = models.notes.delete().where(models.notes.c.id == note_id, models.notes.c.user_id == current_user.id)
    await database.execute(delete_query)
    return {"detail": "Note deleted successfully"}