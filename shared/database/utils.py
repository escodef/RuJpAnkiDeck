import logging

from .models import TranslationTable, ExampleTable
from .db_session import SessionLocal 

def save_to_sqlite(dictionary):
    logging.debug('save_to_sqlite()')
    session = SessionLocal()
    logging.debug('save_to_sqlite(): got session')
    try:
        for item in dictionary:
            db_translation = TranslationTable(
                word=item.word,
                reading=item.reading,
                mainsense=item.mainsense,
                senses=item.senses
            )
            for ex in item.examples:
                db_translation.examples.append(
                    ExampleTable(ja=ex.ja, re=ex.re, tr=ex.tr)
                )
            session.add(db_translation)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()