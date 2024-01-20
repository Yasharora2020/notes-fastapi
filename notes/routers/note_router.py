from fastapi import APIRouter, HTTPException
from .. import models, schemas
from ..database import database

router = APIRouter()

@router.post("/notes/", response_model=schemas.Note)
async def create_note(note: schemas.NoteCreate):
    query = models.notes.insert().values(title=note.title, content=note.content)
    last_record_id = await database.execute(query)
    return {**note.dict(), "id": last_record_id}

@router.get("/notes/", response_model=list[schemas.Note])
async def read_notes(skip: int = 0, limit: int = 10):
    query = models.notes.select().offset(skip).limit(limit)
    return await database.fetch_all(query)

@router.get("/notes/{note_id}", response_model=schemas.Note)
async def read_note(note_id: int):
    query = models.notes.select().where(models.notes.c.id == note_id)
    note = await database.fetch_one(query)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/notes/{note_id}", response_model=schemas.Note)
async def update_note(note_id: int, note: schemas.NoteCreate):
    # Check if note exists
    select_query = models.notes.select().where(models.notes.c.id == note_id)
    existing_note = await database.fetch_one(select_query)
    if existing_note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    # Update note
    update_query = models.notes.update().where(models.notes.c.id == note_id).values(title=note.title, content=note.content)
    await database.execute(update_query)
    return {**note.dict(), "id": note_id}

@router.delete("/notes/{note_id}", response_model=dict)
async def delete_note(note_id: int):
    delete_query = models.notes.delete().where(models.notes.c.id == note_id)
    await database.execute(delete_query)
    return {"detail": "Note deleted successfully"}
