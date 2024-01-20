
# File: __init__.py


# File: database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# File: dependencies.py

from .database import SessionLocal


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# File: init_db.py

from database import engine
from models import Base


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()

# File: models.py

from sqlalchemy import Column, Integer, String
from .database import Base


class NoteModel(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, index=True)

# File: schemas.py

from pydantic import BaseModel


class Note(BaseModel):
    title: str
    content: str


class NoteCreate(BaseModel):
    title: str
    content: str


# File:routers/note_router.py
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
