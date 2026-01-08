import logging
from shared.database.db_session import init_db, SessionLocal
from shared.database.utils import save_to_sqlite
from shared.csv.utils import get_words
from core.processor import DictionaryProcessor


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/parser.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def main():
    init_db()
    session = SessionLocal()
    try:
        words_to_parse = get_words()
        parser = DictionaryProcessor()
        parser.parse_words(words_to_parse[:15000])
        save_to_sqlite(parser.dictionary)

        logging.info("Parse done")
    finally:
        session.close()
        logging.info("Session closed.")


if __name__ == "__main__":
    main()
