import requests
import html2text
import logging
import pykakasi

from typing import List
from bs4 import BeautifulSoup
from models.models import Example



class ExampleParser():
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:145.0) Gecko/20100101 Firefox/145.0'
        })
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_emphasis = True
        self.h2t.ignore_tables = True
        self.kks = pykakasi.kakasi()


    def parse_word(self, word: str) -> List[Example]:
        try:
            url = f"https://www.jardic.ru/search/search_r.php?q={word}&pg=0&dic_tatoeba=1&sw=1472"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            examples = []
            
            tab = soup.find(id="tabContent")

            if not tab:
                self.logger.debug(f"No tabContent found for word: {word}")
                return None

            rows = tab.select("tr")
            if not rows:
                self.logger.debug(f"No rows in tab for word: {word}")
                return None
            
            self.logger.debug(len(rows))
            
            for row in rows[:5:2]:
                self.logger.debug(str(row))

                td = row.find("td") or row.select_one('td[id^="word-"]')
            
                if not td:
                    self.logger.debug(f"No matching td in row for word: {word}")
                    continue
                
                text: str = self.h2t.handle(str(td))

                
                if text:
                    self.logger.debug(text)

                    sents = text.split('\n')

                    ja = sents[0].strip()
                    tr = sents[1].strip()
                    re = ''
                    kks = self.kks.convert(ja)

                    for item in kks:
                        re += item['hira']
                    
                    example = Example(
                        ja=ja,
                        re=re,
                        tr=tr
                    )

                    examples.append(example)
            return examples
            
        except Exception as e:
            self.logger.error(f"Failed to parse {word}: {e}")
            raise
