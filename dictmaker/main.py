import os
import logging
import traceback
import sys
import signal

from typing import List
from models.models import DictionaryList
from parsers.word_parser import WordParser
from parsers.gui_word_parser import WordParserGUI
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database.db_session import init_db, SessionLocal
from shared.database.utils import save_to_sqlite, get_by_index
from shared.csv.utils import get_words

dict_url = os.getenv("DICT_URL")
jardic_path = os.getenv("JARDIC_PATH")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/parser.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
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
        for index, word in enumerate(words):
            if not self.running:
                break
            try:
                is_parsed_before = get_by_index(index)
                if len(is_parsed_before) > 0:
                    continue
                logging.info(f"Parsing word: {word[0]}")
                
                if self.is_windows and self.gui_parser:
                    translations = self.gui_parser.parse_word(word)
                else:
                    translations = self.parser.parse_word(word)

                if translations is None: 
                    continue

                logging.info(translations)
                
                for translation in translations:
                    translation.index_csv = index
                    self.dictionary.append(translation)
                if len(translations) == 0:
                    logging.warning(f"translations len: {len(translations)} for word {word[0]} at index {index}")
                    # break
                
                
            except Exception as e:
                logging.error(f"Error when parsing {word[0]}: {e}")
                logging.error(traceback.format_exc())
                continue

        save_to_sqlite(self.dictionary)
        return self.dictionary


def main():
    init_db()
    session = SessionLocal()
    try:
        words_to_parse = get_words()
        parser = JapaneseDictionaryParser()
        dictionary = parser.parse_words(words_to_parse[:2500])

        logging.info(f"Parsed words: {len(dictionary)}")
    finally:
        session.close()
        logging.info("Session closed.")
    

if __name__ == "__main__":
    main()