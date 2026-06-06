import sys
import signal
import logging

from shared.config import JARDIC_PATH, DICT_URL
from shared.database.db_session import init_db, SessionLocal
from shared.database.utils import save_to_sqlite
from shared.csv import get_words
from core.processor import DictionaryProcessor
from parsers.gui_word_parser import WordParserGUI
from parsers.word_parser import WordParser


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("dictmaker/logs/parser.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def main():
    init_db()

    session = SessionLocal()

    is_windows = sys.platform == "win32"
    if is_windows:
        logging.info("Using GUI Parser (Windows)")
        parser = WordParserGUI(JARDIC_PATH)
    else:
        logging.info("Using Web Parser (Non-Windows)")
        parser = WordParser(DICT_URL)

    processor = DictionaryProcessor(parser=parser, session=session)

    def signal_handler(signum, frame):
        logging.info("Gracefully shutting down...")
        processor.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        words_to_parse = get_words()
        processor.parse_words(words_to_parse[:25000])

        if processor.dictionary:
            save_to_sqlite(processor.dictionary, session=session)
            session.commit()

        logging.info("Parse completed successfully.")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
    finally:
        session.close()
        logging.info("Session closed.")


if __name__ == "__main__":
    main()
