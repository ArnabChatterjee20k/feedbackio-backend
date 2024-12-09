import os
from sqlalchemy import create_engine,text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker,DeclarativeBase
DB_URL = os.environ.get("DB_URL")
engine  = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
class Base(DeclarativeBase):
    pass

def create_models():
    test_database_connection()
    Base.metadata.create_all(bind=engine)

def test_database_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("Database is connected!")
            return True
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return False
