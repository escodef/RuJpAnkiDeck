import pytest
import logging
import pykakasi
from parsers.gui_word_parser import WordParserGUI


@pytest.fixture
def parser():
    obj = WordParserGUI.__new__(WordParserGUI)
    obj.logger = logging
    obj.kks = pykakasi.kakasi()
    obj.yarxi_pattern = r"^\[[a-zA-Z]+\]$"

    return obj


def test_basic_article_ra(parser):
    test_article = """…ら
…等
суф. мн. числа; после имени собств. и другие; и его друзья (сторонники); и иже с ним, и его присные; и сопровождающие его лица.
"""

    result = parser.is_article_correct(test_article, "ら", "ラ")

    assert result is True


def test_basic_article_check(parser):
    test_article = """チェックする
1. проверять (англ. to check)
2. отмечать, помечать
3. препятствовать, тормозить"""

    result = parser.is_article_correct(test_article, "チェックする", "チェックスル")

    assert result is True


def test_basic_article_kouchiku(parser):
    test_article = """こうちく　　
構築
сооружение, постройка, строительство;
～する сооружать, строить, воздвигать."""

    result = parser.is_article_correct(test_article, "構築する", "コウチクスル")

    assert result is True


def test_basic_article_han(parser):
    test_article = """たん　　　　
反･段
1) тан (мера длины для тканей = 10,6 м);
2) тан см. <<たんぶ>>."""

    result = parser.is_article_correct(test_article, "反", "ハン")

    assert result is True


def test_yarxi_simple_article(parser):
    test_article = """東口
[higashiguchi]
восточный вход (выход)

TN57062"""

    result = parser.is_article_correct(test_article, "東口", "ヒガシグチ")

    assert result is True
