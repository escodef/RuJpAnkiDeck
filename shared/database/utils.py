from .models import TranslationTable, ExampleTable
from .db_session import SessionLocal

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


def get_by_word_or_reading(word: str, reading: str) -> list[TranslationTable]:
    session = SessionLocal()
    try:
        result = session.query(TranslationTable).filter(
            TranslationTable.word == word
        ).first()

        if result:
            return [result]

        results = session.query(TranslationTable).filter(
            TranslationTable.reading == reading
        ).limit(3).all()
        
        return results
    finally:
        session.close()

def get_by_word(word: str) -> TranslationTable | None:
    session = SessionLocal()
    try:
        results = session.query(TranslationTable).filter(
            TranslationTable.word == word,
        ).first()
        return results
    finally:
        session.close()

def get_by_reading(reading: str) -> TranslationTable | None:
    session = SessionLocal()
    try:
        results = session.query(TranslationTable).filter(
            TranslationTable.reading == reading,
        ).first()
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