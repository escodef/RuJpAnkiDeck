import os
import sys
import logging
import traceback
import signal
from dotenv import load_dotenv

load_dotenv()
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)

from typing import List
from models.models import DictionaryList
from parsers.word_parser import WordParser
from parsers.gui_word_parser import WordParserGUI

from shared.database.db_session import init_db, SessionLocal
from shared.database.utils import (
    save_to_sqlite,
    get_by_index,
    get_by_reading,
    get_by_word_and_reading,
    add_not_found,
    get_not_found,
)
from shared.csv.utils import get_words
from shared.regex.utils import has_kanji
from shared.kakashi.utils import get_hiragana


dict_url = os.getenv("DICT_URL")
jardic_path = os.getenv("JARDIC_PATH")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/parser.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


class JapaneseDictionaryParser:
    def __init__(self):
        self.is_windows = sys.platform == "win32"
        self.parser = WordParser(dict_url)
        self.running = True

        if self.is_windows:
            self.gui_parser = WordParserGUI(jardic_path)
        else:
            self.gui_parser = None

        self.dictionary: DictionaryList = list()

        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)

    def _handle_exit(self, signum, frame):
        logging.info("Gracefully shutting down...")
        self.running = False

    def parse_words(self, words: List[List[str]]) -> DictionaryList:
        batch_size = 50
        for index, wordcsv in enumerate(words):
            if not self.running:
                save_to_sqlite(self.dictionary)
                break
            word, _, reading_raw = wordcsv[:3]
            try:
                exists = None
                reading = get_hiragana(reading_raw)
                if has_kanji(word):
                    exists = get_by_word_and_reading(word, reading)
                else:
                    exists = get_by_reading(reading)

                if not exists:
                    exists = get_not_found(word, reading_raw)

                is_parsed_before = get_by_index(index)
                if len(is_parsed_before) > 0 or exists:
                    continue
                logging.info(f"Parsing word: {word} at index {index}")

                if self.is_windows and self.gui_parser:
                    translations = self.gui_parser.parse_word(wordcsv)
                else:
                    translations = self.parser.parse_word(wordcsv)

                if translations is None:
                    continue

                logging.info(f"found translations: {translations}")

                for translation in translations:
                    is_duplicate_in_batch = any(
                        t.word == translation.word for t in self.dictionary
                    )
                    if not is_duplicate_in_batch:
                        translation.index_csv = index
                        self.dictionary.append(translation)
                    else:
                        logging.warning(
                            f"found dup translation: {translation} for word {word} at index {index}"
                        )

                if len(translations) == 0:
                    logging.warning(
                        f"translations len: {len(translations)} for word {word} at index {index}"
                    )
                    add_not_found(word, reading_raw)

                if len(self.dictionary) >= batch_size:
                    save_to_sqlite(self.dictionary)
                    self.dictionary.clear()
                    logging.info("Batch saved to database.")

            except Exception as e:
                logging.error(f"Error when parsing {word[0]}: {e}")
                logging.error(traceback.format_exc())
                continue


def main():
    init_db()
    session = SessionLocal()
    try:
        words_to_parse = get_words()
        parser = JapaneseDictionaryParser()
        parser.parse_words(words_to_parse[:2000])
        save_to_sqlite(parser.dictionary)

        logging.info("Parse done")
    finally:
        session.close()
        logging.info("Session closed.")


if __name__ == "__main__":
    main()
