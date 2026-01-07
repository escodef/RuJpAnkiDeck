from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TranslationTable(Base):
    __tablename__ = "translations"
    id = Column(Integer, primary_key=True)
    word = Column(String, index=True)
    reading = Column(String, index=True)
    mainsense = Column(String)
    senses = Column(String)
    index_csv = Column(Integer)

    examples = relationship("ExampleTable", back_populates="translation", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("word", "reading", name="_word_reading_uc"),)


class ExampleTable(Base):
    __tablename__ = "examples"
    id = Column(Integer, primary_key=True)
    ja = Column(String)
    re = Column(String)
    tr = Column(String)
    translation_id = Column(Integer, ForeignKey("translations.id"))
    translation = relationship("TranslationTable", back_populates="examples")


class NotFoundTable(Base):
    __tablename__ = "not_found"
    id = Column(Integer, primary_key=True)
    word = Column(String)
    reading = Column(String)
