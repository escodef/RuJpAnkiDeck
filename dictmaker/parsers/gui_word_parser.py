import time
import logging
import pyperclip
import pykakasi
import re

from typing import List
from pywinauto import Desktop, Application
from models.models import Translation
from pywinauto.keyboard import send_keys
from shared.regex.utils import has_cyrillic


class WordParserGUI:
    def __init__(self, jardic_path: str):
        self.logger = logging.getLogger(__name__)
        self.app = Application(backend="uia").start(jardic_path)

        self.win = Desktop(backend="uia").window(title_re=".*Jardic.*")
        self.win.wait("visible", timeout=10)
        self.kks = pykakasi.kakasi()

    def switch_tab(self, tab_index: int):
        tab_ctrl = self.win.child_window(control_type="Tab")
        tab_items = tab_ctrl.children(control_type="TabItem")

        if tab_index < 0 or tab_index >= len(tab_items):
            self.logger.error(f"Tab index {tab_index} out of range")
            return

        tab_item = tab_items[tab_index]
        tab_item.select()
        time.sleep(0.5)

    def parse_word(self, wordcsv: List[str]) -> List[Translation] | None:
        kata = wordcsv[2]
        reading = ""
        kks = self.kks.convert(kata)

        for item in kks:
            reading += item["hira"]

        self.logger.debug(f"Got reading {reading}")

        try:
            input_box = self.win.child_window(auto_id="202", control_type="Edit")
            self.switch_tab(1)
            self.win.set_focus()

            input_box.set_edit_text("")
            input_box.type_keys(reading, with_spaces=True)
            time.sleep(0.5)

            pane = self.win.child_window(control_id=201)
            table = self.win.child_window(control_id=100)

            last_reading = ""
            while True:
                pane.set_focus()
                pane.click_input()
                send_keys("^a^c")
                current_reading = pyperclip.paste().strip().splitlines()[0]

                variants = [v.strip() for v in current_reading.split("・")]

                if current_reading == last_reading or (
                    reading not in variants and kata not in variants and f"…{reading}" not in variants
                ):
                    if reading not in variants and kata not in variants and f"…{reading}" not in variants:
                        table.set_focus()
                        send_keys("{VK_DOWN}")
                    break

                last_reading = current_reading
                table.set_focus()
                send_keys("{VK_UP}")

            results: list[str] = []
            last_text = ""
            while True:
                pane.set_focus()
                pane.click_input()
                send_keys("^a^c")
                current_text = pyperclip.paste().strip()
                current_reading = current_text.splitlines()[0]
                variants = [v.strip() for v in current_reading.split("・")]
                self.logger.debug(f"Variants {variants}")

                if current_text == last_text or (
                    reading not in variants and kata not in variants and f"…{reading}" not in variants
                ):
                    break

                dot_count = current_text.splitlines()[1].count("・")

                results.append(current_text)
                last_text = current_text
                table.set_focus()
                for _ in range(dot_count + 1):
                    send_keys("{VK_DOWN}")

            return self.process_results(results)

        except Exception as e:
            self.logger.error(f"parse_word(): {e}")
            return None

    def process_results(self, results: list[str]) -> List[Translation]:
        ts: List[Translation] = []
        for entry in results:
            entry = entry.replace("\r", "")
            sents = entry.split("\n")
            strip = 1
            reading = entry.splitlines()[0].strip()

            if not has_cyrillic(sents[1]):
                word = sents[1]
                strip = 2
            else:
                word = reading

            senses = "\n".join(sents[strip:]).strip()
            if senses.startswith('см. ') or ' см. ' in senses:
                continue
            
            mainsense = self.get_mainsense(senses)

            t = Translation(
                word=word, reading=reading, mainsense=mainsense, senses=senses
            )

            ts.append(t)

        return ts

    def get_mainsense(self, article: str) -> str:
        match = re.search(r"\d+[\.\)]:?\s+([^;:\n]+)", article)

        if match:
            return match.group(1).strip()

        return article.split(";")[0].strip()
