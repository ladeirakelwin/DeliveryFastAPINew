from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeBase
from dependencies import DATABASE_URL
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autoflush=False, bind=engine)

Base: DeclarativeBase = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DBSession = Annotated[Session, Depends(get_db)]
