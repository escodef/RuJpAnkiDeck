from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import mapped_column, relationship, DeclarativeBase, Mapped


class Base(DeclarativeBase):
    pass


class TranslationTable(Base):
    __tablename__ = "translations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    word: Mapped[str] = mapped_column(String, index=True)
    reading: Mapped[str] = mapped_column(String, index=True)
    mainsense: Mapped[str] = mapped_column(String)
    senses: Mapped[str] = mapped_column(String)
    index_csv: Mapped[int | None] = mapped_column(Integer, index=True)

    examples: Mapped[list["ExampleTable"]] = relationship(
        "ExampleTable", back_populates="translation", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("word", "reading", name="_word_reading_uc"),)


class ExampleTable(Base):
    __tablename__ = "examples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ja: Mapped[str] = mapped_column(String)
    re: Mapped[str] = mapped_column(String)
    tr: Mapped[str] = mapped_column(String)

    translation_id: Mapped[int] = mapped_column(Integer, ForeignKey("translations.id"))
    translation: Mapped["TranslationTable"] = relationship(
        "TranslationTable", back_populates="examples"
    )


class NotFoundTable(Base):
    __tablename__ = "not_found"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    word: Mapped[str] = mapped_column(String)
    reading: Mapped[str] = mapped_column(String)
