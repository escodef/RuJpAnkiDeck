from .models import TranslationTable, ExampleTable, NotFoundTable
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
                index_csv=item.index_csv,
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


def add_not_found(word, reading):
    session = SessionLocal()
    try:
        db_translation = NotFoundTable(
            word=word,
            reading=reading,
        )
        session.add(db_translation)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_not_found(word, reading):
    session = SessionLocal()
    try:
        result = (
            session.query(NotFoundTable)
            .filter(NotFoundTable.word == word, NotFoundTable.reading == reading)
            .first()
        )

        return result
    finally:
        session.close()


def get_by_word_or_reading(word: str, reading: str, limit=3) -> list[TranslationTable]:
    session = SessionLocal()
    try:
        result = (
            session.query(TranslationTable)
            .filter(
                TranslationTable.word.contains(word),
                TranslationTable.reading == reading,
            )
            .first()
        )

        if result:
            return [result]

        results = (
            session.query(TranslationTable)
            .filter(TranslationTable.reading == reading)
            .limit(limit)
            .all()
        )

        return results
    finally:
        session.close()


def get_by_word_and_reading(word: str, reading: str) -> TranslationTable | None:
    session = SessionLocal()
    try:
        results = (
            session.query(TranslationTable)
            .filter(
                TranslationTable.word.contains(word),
                TranslationTable.reading == reading,
            )
            .first()
        )
        return results
    finally:
        session.close()


def get_by_word(word: str) -> TranslationTable | None:
    session = SessionLocal()
    try:
        results = (
            session.query(TranslationTable)
            .filter(
                TranslationTable.word == word,
            )
            .first()
        )
        return results
    finally:
        session.close()


def get_by_reading(reading: str, limit=3) -> list[TranslationTable]:
    session = SessionLocal()
    try:
        pattern_start = f"{reading}・%"
        pattern_end = f"%・{reading}"
        pattern_middle = f"%・{reading}・%"
        pattern_start_spaced = f"{reading} ・%"
        pattern_end_spaced = f"%・ {reading}"
        pattern_middle_spaced = f"%・ {reading} ・%"

        results = (
            session.query(TranslationTable)
            .filter(
                or_(
                    TranslationTable.reading == reading,
                    TranslationTable.reading.like(pattern_start),
                    TranslationTable.reading.like(pattern_end),
                    TranslationTable.reading.like(pattern_middle),
                    TranslationTable.reading.like(pattern_start_spaced),
                    TranslationTable.reading.like(pattern_end_spaced),
                    TranslationTable.reading.like(pattern_middle_spaced),
                )
            )
            .limit(limit)
            .all()
        )
        return results
    finally:
        session.close()


def get_by_index(query: int) -> list[TranslationTable]:
    session = SessionLocal()
    try:
        results = (
            session.query(TranslationTable)
            .filter(TranslationTable.index_csv == query)
            .all()
        )
        return results
    finally:
        session.close()

def get_all_parsed_indexes() -> set[int]:
    session = SessionLocal()
    try:
        results = session.query(TranslationTable.index_csv).distinct().all()
        return {r[0] for r in results if r[0] is not None}
    finally:
        session.close()