import logging
import re

from typing import List
from pykakasi import kakasi
from pywinauto import Application
from pywinauto.controls.uia_controls import ListViewWrapper
from pywinauto.findwindows import ElementNotFoundError
from models.models import Translation
from shared.regex.utils import has_cyrillic, has_kanji, split_by_dots


class WordParserGUI:
    def __init__(self, jardic_path: str):
        self.logger = logging.getLogger(__name__)
        try:
            self.app = Application(backend="uia").connect(
                title_re=".*Jardic.*", timeout=2
            )
        except (ElementNotFoundError, Exception):
            self.logger.debug("App not found. Starting up...")
            Application(backend="uia").start(jardic_path)
            self.app = Application(backend="uia").connect(
                title_re=".*Jardic.*", timeout=10
            )

        self.win = self.app.window(title_re=".*Jardic.*")
        self.win.wait("ready", timeout=10)
        self.kks = kakasi()

        self.yarxi_pattern = r"^\[[a-zA-Z]+\]$"

    def switch_tab(self, tab_index: int):
        tab_ctrl = self.win.child_window(control_type="Tab")
        tab_items = tab_ctrl.children(control_type="TabItem")

        if tab_index < 0 or tab_index >= len(tab_items):
            self.logger.error(f"Tab index {tab_index} out of range")
            return

        tab_item = tab_items[tab_index]
        tab_item.select()

    def parse_word(self, wordcsv: List[str]) -> List[Translation] | None:
        word = wordcsv[0]
        kata = wordcsv[2]

        try:
            input_box = self.win.child_window(auto_id="202", control_type="Edit")
            input_box.set_edit_text("")

            tab_idx = 2 if has_kanji(word) else 1
            self.switch_tab(tab_idx)
            input_box.type_keys(word, with_spaces=True)
            pane = self.win.child_window(control_id=201)
            table = self.win.child_window(control_id=100)
            table_obj: ListViewWrapper = table.wrapper_object()

            last_article = ""
            while True:
                current_article = pane.get_value().replace("\r", "\n").strip()

                is_article_correct = self.is_article_correct(
                    current_article, word, kata
                )

                if not is_article_correct:
                    if current_article != last_article:
                        table_obj.type_keys("{VK_DOWN}")
                    break

                last_article = current_article
                table_obj.type_keys("{VK_UP}")

            results: list[str] = []

            last_article = ""
            while True:
                current_article = pane.get_value().replace("\r", "\n").strip()
                is_article_correct = self.is_article_correct(
                    current_article, word, kata
                )

                if not is_article_correct:
                    break

                results.append(current_article)
                last_article = current_article
                table_obj.type_keys("{VK_DOWN}")

            return self.process_results(results)

        except Exception as e:
            self.logger.error(f"parse_word(): {e}")
            raise e

    def process_results(self, results: list[str]) -> List[Translation]:
        ts: List[Translation] = []
        for entry in results:
            entry = entry.replace("\r", "")
            sents = entry.split("\n")
            strip = 1

            if re.match(self.yarxi_pattern, sents[1]):
                word = sents[0]
                reading = "".join(
                    [
                        item["kana"]
                        for item in self.kks.convert(
                            sents[1].replace("[", "").replace("]", "")
                        )
                    ]
                )

            else:
                reading = entry.splitlines()[0].strip()
                if not has_cyrillic(sents[1]):
                    word = sents[1]
                    strip = 2
                else:
                    word = reading

            senses = "\n".join(sents[strip:]).strip()
            is_article_recur = senses.startswith("см. ") or " см. " in sents[strip:][0]

            if is_article_recur:
                continue

            mainsense = self.get_mainsense(senses)

            t = Translation(
                word=word, reading=reading, mainsense=mainsense, senses=senses
            )

            ts.append(t)

        return ts

    def get_mainsense(self, article: str) -> str:
        match = re.search(r"\d+[\.\)]:?\s+([^:\n]+)", article)

        if match:
            senses = match.group(1).strip().split(";")
        else:
            senses = article.split(";")

        part = senses[0].strip()
        result = part.partition(":")[-1].strip() or part.strip()
        i = 1
        while i < len(senses):
            part = senses[i].strip()
            if len(result + part) > 25 or not part:
                break
            result = result + ", " + (part.partition(":")[-1].strip() or part.strip())
            i = i + 1

        return (
            result
            if result.count("(") == result.count(")")
            else result.replace("(", "").replace(")", "")
        )

    def is_article_correct(self, article_text: str, word: str, kata: str) -> bool:
        lines = article_text.splitlines()
        if not lines:
            return False

        if re.match(self.yarxi_pattern, lines[1]):
            kana_line = "".join(
                [
                    item["kana"]
                    for item in self.kks.convert(
                        lines[1].replace("[", "").replace("]", "")
                    )
                ]
            )
            kanji_line = lines[0].split()[0] if has_kanji(lines[0]) else ""
            kana_variants = [kana_line]
            kanji_variants = [kanji_line.strip()]
        else:
            kana_line = lines[0]
            kanji_line = lines[1] if has_kanji(lines[1]) else ""
            kana_variants = [v.strip() for v in split_by_dots(kana_line)]
            kanji_variants = [v.strip() for v in split_by_dots(kanji_line)]

        self.logger.debug(f"kana_variants {kana_variants}")
        self.logger.debug(f"kanji_variants {kanji_variants}")

        reading = "".join([item["hira"] for item in self.kks.convert(kata)])

        self.logger.debug(f"Got reading {reading}")

        reading_ok = (
            reading in kana_variants
            or kata in kana_variants
            or word in kana_variants
            or f"…{reading}" in kana_variants
            or f"{reading}…" in kana_variants
            or (
                reading.endswith("する")
                and len(reading) > 2
                and reading.removesuffix("する") in kana_variants
            )
        )

        kanji_ok = word in kanji_variants

        if reading_ok or kanji_ok:
            return True

        self.logger.debug(
            f"Article {article_text} incorrect for word {word} with reading {reading} and kata {kata}"
        )
        return False
