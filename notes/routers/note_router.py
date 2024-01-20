from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..dependencies import get_db
from .. import models, schemas

router = APIRouter()


@router.post("/notes/", response_model=schemas.Note)
def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    db_note = models.NoteModel(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.get("/notes/", response_model=list[schemas.Note])
def read_notes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    notes = db.query(models.NoteModel).offset(skip).limit(limit).all()
    return notes


@router.get("/notes/{note_id}", response_model=schemas.Note)
def read_note(note_id: int, db: Session = Depends(get_db)):
    db_note = db.query(models.NoteModel).filter(models.NoteModel.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note


@router.put("/notes/{note_id}", response_model=schemas.Note)
def update_note(note_id: int, note: schemas.NoteCreate, db: Session = Depends(get_db)):
    db_note = db.query(models.NoteModel).filter(models.NoteModel.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    db_note.title = note.title
    db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    return db_note


@router.delete("/notes/{note_id}", response_model=schemas.Note)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    db_note = db.query(models.NoteModel).filter(models.NoteModel.id == note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(db_note)
    db.commit()
    return db_note
