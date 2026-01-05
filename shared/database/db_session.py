import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_path = os.getenv("DB_PATH", "dictionary.db")
engine = create_engine(f"sqlite:///{db_path}")
SessionLocal = sessionmaker(bind=engine)


def init_db():
    from .models import Base

    Base.metadata.create_all(engine)
