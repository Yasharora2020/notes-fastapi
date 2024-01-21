from databases import Database
from sqlalchemy import create_engine


DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, echo=True)

database = Database(DATABASE_URL)
