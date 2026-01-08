import sys
import os
import logging
import traceback
import re
from dotenv import load_dotenv
from shared.database.utils import (
    save_to_sqlite,
    get_by_index,
    get_by_reading,
    get_by_word_and_reading,
    add_not_found,
    get_not_found,
)
from shared.regex.utils import has_kanji
from shared.kakashi.utils import get_hiragana

from typing import List
from models.models import DictionaryList
from parsers.word_parser import WordParser
from parsers.gui_word_parser import WordParserGUI

load_dotenv()

dict_url = os.getenv("DICT_URL")
jardic_path = os.getenv("JARDIC_PATH")


class DictionaryProcessor:
    def __init__(self):
        self.is_windows = sys.platform == "win32"
        self.parser = WordParser(dict_url)
        self.running = True

        if self.is_windows:
            self.gui_parser = WordParserGUI(jardic_path)
        else:
            self.gui_parser = None

        self.dictionary: DictionaryList = list()

    def stop(self):
        self.running = False

    def _get_variants(self, text: str) -> set[str]:
        if not text:
            return set()
        return {v.strip() for v in re.split(r"・|･", text) if v.strip()}

    def is_duplicate_translation(
        self, translation, seen_set: set[tuple[str, str]]
    ) -> bool:
        new_words = self._get_variants(translation.word)
        new_reading = translation.reading

        for w in new_words:
            if (w.strip("…"), new_reading.strip("…")) in seen_set:
                return True
        return False

    def _add_to_seen(self, translation, seen_set: set[tuple[str, str]]):
        new_words = self._get_variants(translation.word)
        new_reading = translation.reading
        for w in new_words:
            clean_word = w.strip("…")
            clean_reading = new_reading.strip("…")
            seen_set.add((clean_word, clean_reading))

    def parse_words(self, words: List[List[str]]) -> DictionaryList:
        batch_size = 50
        seen_in_batch = set()
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
                    if not self.is_duplicate_translation(translation, seen_in_batch):
                        translation.index_csv = index
                        self.dictionary.append(translation)
                        self._add_to_seen(translation, seen_in_batch)
                    else:
                        logging.warning(f"found dup translation: {translation.word}...")

                if len(translations) == 0:
                    logging.warning(
                        f"translations len: {len(translations)} for word {word} at index {index}"
                    )
                    add_not_found(word, reading_raw)

                if len(self.dictionary) >= batch_size:
                    save_to_sqlite(self.dictionary)
                    self.dictionary.clear()
                    seen_in_batch.clear()
                    logging.info("Batch saved to database.")

            except Exception as e:
                logging.error(f"Error when parsing {word[0]}: {e}")
                logging.error(traceback.format_exc())
                continue
