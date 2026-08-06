from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dependencies import DATABASE_URL
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated


same_thread = False if "sqlite" in DATABASE_URL else True
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": same_thread})

SessionLocal = sessionmaker(autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DBSession = Annotated[Session, Depends(get_db)]
