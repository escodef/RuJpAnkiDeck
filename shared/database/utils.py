from .models import TranslationTable, ExampleTable
from .db_session import SessionLocal
from sqlalchemy import or_

def save_to_sqlite(dictionary):
    session = SessionLocal()
    try:
        for item in dictionary:
            db_translation = TranslationTable(
                word=item.word,
                reading=item.reading,
                mainsense=item.mainsense,
                senses=item.senses,
                index_csv=item.index_csv
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

def get_by_reading(query):
    session = SessionLocal()
    try:
        results = session.query(TranslationTable).filter(
            or_(
                TranslationTable.word.contains(query),
                TranslationTable.reading.contains(query)
            )
        ).all()
        return results
    finally:
        session.close()

def get_by_index(query: int):
    session = SessionLocal()
    try:
        results = session.query(TranslationTable).filter(
            TranslationTable.index_csv == query 
        ).all()
        return results
    finally:
        session.close()