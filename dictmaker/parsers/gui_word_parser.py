import time
import logging
import pyperclip
import pykakasi
import re

from typing import List
from pywinauto import Desktop, Application
from models.models import Translation
from pywinauto.keyboard import send_keys
from shared.database.utils import get_by_word
from utils.re_utils import has_cyrillic

class WordParserGUI:
    def __init__(self, jardic_path: str):
        self.logger = logging.getLogger(__name__)
        self.app = Application(backend="uia").start(jardic_path)
        time.sleep(1)

        self.win = Desktop(backend="uia").window(title_re=".*Jardic.*")
        self.win.wait("visible", timeout=10)
        self.kks = pykakasi.kakasi()


    def switch_tab(self, tab_index: int):
        """Переключение на вкладку по индексу (0, 1, 2, ...)"""
        tab_ctrl = self.win.child_window(control_type="Tab")
        tab_items = tab_ctrl.children(control_type="TabItem")

        if tab_index < 0 or tab_index >= len(tab_items):
            self.logger.error(f"Tab index {tab_index} out of range")
            return

        tab_item = tab_items[tab_index]
        tab_item.select()
        time.sleep(0.5)  

    def parse_word(self, wordcsv: List[str]) -> List[Translation] | None:
        word = wordcsv[0]
        kata = wordcsv[2]
        re = ''
        kks = self.kks.convert(kata)
        ts: List[Translation] = []

        for item in kks:
            re += item['hira']
        
        self.logger.debug(f"Got reading {re}")

        try:
            input_box = self.win.child_window(auto_id="202", control_type="Edit")
            self.switch_tab(1)
            self.win.set_focus()
            
            input_box.set_edit_text("")
            input_box.type_keys(re, with_spaces=True)
            time.sleep(0.5)

            pane = self.win.child_window(control_id=201)
            table = self.win.child_window(control_id=100)

            last_re = ""
            while True:
                pane.set_focus()
                pane.click_input()
                send_keys('^a^c')
                current_re = pyperclip.paste().strip().splitlines()[0]

                variants = [v.strip() for v in current_re.split('・')]
                
                if current_re == last_re or (re not in variants and kata not in variants):
                    if re not in variants and kata not in variants:
                        table.set_focus()
                        send_keys('{VK_DOWN}')
                    break
                
                last_re = current_re
                table.set_focus()
                send_keys('{VK_UP}')
                time.sleep(0.1)

            results: list[str] = []
            last_text = ""
            while True:
                pane.set_focus()
                pane.click_input()
                send_keys('^a^c')
                current_text = pyperclip.paste().strip()
                current_re = current_text.splitlines()[0]
                variants = [v.strip() for v in current_re.split('・')]
                self.logger.debug(f"Variants {variants}")

                if current_text == last_text or (re not in variants and kata not in variants):
                    break

                dot_count = current_text.splitlines()[1].count("・")


                results.append(current_text)
                last_text = current_text
                table.set_focus()
                for _ in range(dot_count + 1):
                    send_keys('{VK_DOWN}')
                time.sleep(0.1)


            for entry in results:
                sents = entry.split('\n')
                strip = 1

                if not has_cyrillic(sents[1]):
                    word = sents[1]
                    strip = 2 
                
                exists = get_by_word(word)
                if exists: 
                    continue

                senses = "\n".join(sents[strip:]).strip()
                
                mainsense = self.get_mainsense(senses)

                t = Translation(
                        word=word,
                        reading=re,
                        mainsense=mainsense,
                        senses=senses
                    )
                
                ts.append(t)

            return ts

        except Exception as e:
            self.logger.error(f"parse_word(): {e}")
            return None

    def get_mainsense(self, article: str) -> str:
        processed_result = ''

        if re.search(r'^\d+\.', article.strip(), re.MULTILINE):
            items = re.findall(r'\d+\.\s*([^;\n]+)', article)
            processed_result = items[0] 
        else:
            processed_result = article.split(';')[0].strip()

        return processed_result