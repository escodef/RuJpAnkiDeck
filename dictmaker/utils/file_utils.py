import os
import logging

from models.models import Base, TranslationTable, ExampleTable, DictionaryList
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_path = os.getenv("DB_PATH", "dictionary.db")
engine = create_engine(f'sqlite:///{db_path}')
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def save_to_sqlite(dictionary: DictionaryList):
    session = Session()
    logging.debug('Started inserting data')
    try:
        for item in dictionary:
            db_translation = TranslationTable(
                word=item.word,
                reading=item.reading,
                mainsense=item.mainsense,
                senses=item.senses
            )
            for ex in item.examples:
                db_translation.examples.append(ExampleTable(ja=ex.ja, re=ex.re, tr=ex.tr))
            session.add(db_translation)
        session.commit()
    finally:
        session.close()
        logging.debug('Done')
