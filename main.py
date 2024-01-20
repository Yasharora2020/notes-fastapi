# main.py
from notes.routers.note_router import router as note_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(note_router)
