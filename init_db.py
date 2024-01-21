from notes.models import metadata
from notes.database import engine

def init_db():
    metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()