from typing import List
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

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

class TranslationTable(Base):
    __tablename__ = 'translations'
    id = Column(Integer, primary_key=True)
    word = Column(String, index=True)
    reading = Column(String)
    mainsense = Column(String)
    senses = Column(String)
    examples = relationship("ExampleTable", back_populates="translation")

class ExampleTable(Base):
    __tablename__ = 'examples'
    id = Column(Integer, primary_key=True)
    ja = Column(String)
    re = Column(String)
    tr = Column(String)
    translation_id = Column(Integer, ForeignKey('translations.id'))
    translation = relationship("TranslationTable", back_populates="examples")
