# Use SQLAlchemy to define models
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.sql.schema import MetaData

metadata = MetaData()


notes = Table(
    "notes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String),
    Column("content", String),
)
