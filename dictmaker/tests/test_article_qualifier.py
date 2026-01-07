import pytest
import logging
import pykakasi
from parsers.gui_word_parser import WordParserGUI


@pytest.fixture
def parser():
    obj = WordParserGUI.__new__(WordParserGUI)
    obj.logger = logging
    obj.kks = pykakasi.kakasi()
    return obj


def test_basic_article_ra(parser):
    test_articles_ra = """…ら
…等
суф. мн. числа; после имени собств. и другие; и его друзья (сторонники); и иже с ним, и его присные; и сопровождающие его лица.
"""

    result = parser.is_article_correct(test_articles_ra, "ら", "ラ")

    assert result is True
