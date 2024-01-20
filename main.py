from fastapi import FastAPI
from notes.database import database
from notes.routers.note_router import router as note_router


app = FastAPI()
app.include_router(note_router)


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
