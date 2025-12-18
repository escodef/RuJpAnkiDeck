from typing import List
from pydantic import BaseModel

class Example(BaseModel):
    ja: str
    re: str
    tr: str

class Translation(BaseModel):
    word: str
    reading: str
    mainsense: str
    senses: str
    examples: List[Example] = []


DictionaryList = List[Translation]