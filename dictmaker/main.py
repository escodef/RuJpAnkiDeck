import csv
import os
import logging
import traceback
import sys

from typing import List
from models.models import DictionaryList
from parsers.word_parser import WordParser
from parsers.gui_word_parser import WordParserGUI
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database.db_session import init_db
from shared.database.utils import save_to_sqlite

csv_name = os.getenv("CSV_FILE")
dict_url = os.getenv("DICT_URL")
jardic_path = os.getenv("JARDIC_PATH")

filter = ["助動詞", "記号", "動詞-接尾", "助詞"]

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
        self.parser = WordParser(dict_url)
        self.gui_parser = WordParserGUI(jardic_path)

        self.dictionary: DictionaryList = list()
    
    def parse_words(self, words: List[List[str]]) -> DictionaryList:
        """Парсит список слов и возвращает словарь"""
        for word in words:
            try:
                logging.info(f"Parsing word: {word[0]}")
                
                translations = self.gui_parser.parse_word(word)
                if translations is None: 
                    continue

                logging.info(translations)
                
                for translation in translations:
                    self.dictionary.append(translation)
                
            except Exception as e:
                logging.error(f"Ошибка при парсинге {word[0]}: {e}")
                logging.error(traceback.format_exc())
                continue

        save_to_sqlite(self.dictionary)
        return self.dictionary

def main():
    init_db()
    words_to_parse = get_words()
    
    parser = JapaneseDictionaryParser()
    dictionary = parser.parse_words(words_to_parse[:1])
    
    logging.info(f"Запарсил слов: {len(dictionary)}")

def get_words() -> List[List[str]]:
    words = []
    with open(csv_name, 'r', newline='', encoding='utf-8') as f:
        csv_file = csv.reader(f)
        for row in csv_file:
            if row[1] in filter or '【' in row[0]:
                continue
            words.append(row)
        return words
    

if __name__ == "__main__":
    main()