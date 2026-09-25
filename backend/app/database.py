'''
# the sqlalchemy engine
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://user:password@localhost:port/database"

engine = create_engine(DATABASE_URL)

# the database session( used to interact with the database that is inside the docker container)
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# the database dependecy
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
'''
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()