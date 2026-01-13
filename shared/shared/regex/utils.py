import re


def has_cyrillic(text):
    return bool(re.search("[\u0400-\u04ff]", text))


def has_kanji(text):
    kanji_regex = r"[\u4E00-\u9FFF]"
    return bool(re.search(kanji_regex, text))

def split_by_dots(text) -> list[str]:
    return re.split(r"・|･", text)