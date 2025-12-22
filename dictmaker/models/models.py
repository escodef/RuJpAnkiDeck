from typing import List, Optional
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
    index_csv: Optional[int] = None
    examples: List[Example] = []

DictionaryList = List[Translation]
