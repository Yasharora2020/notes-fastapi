# Use SQLAlchemy to define models
from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData
from .database import engine


metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True),
    Column("hashed_password", String)
)


notes = Table(
    "notes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String),
    Column("content", String),
    Column("user_id", Integer, ForeignKey("users.id"))

)


