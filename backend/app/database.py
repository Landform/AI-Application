# my-ai-log-viewer/backend/app/database.py
from sqlmodel import create_engine, SQLModel, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Cannot connect to database.")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """
    Creates all tables defined with SQLModel.
    This will ensure 'employee_system_activity' table is created in our new DB.
    """
    SQLModel.metadata.create_all(engine)
    print("Database tables created/checked successfully.")

def get_session():
    """
    Provides a database session for dependency injection in FastAPI.
    """
    with Session(engine) as session:
        yield session