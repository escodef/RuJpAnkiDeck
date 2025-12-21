import os
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

def get_engine():
    db_path = os.getenv("DB_PATH", "dictionary.db") 
    return create_engine(f'sqlite:///{db_path}')

def init_db():
    logging.debug('init_db()')
    Base.metadata.create_all(get_engine())
    logging.debug('init_db() done\n')

SessionLocal = sessionmaker(bind=get_engine())