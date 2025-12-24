import re 

def has_cyrillic(text):
    return bool(re.search('[\u0400-\u04FF]', text))

def has_kanji(text):
    kanji_regex = r'[\u4E00-\u9FFF]'
    return bool(re.search(kanji_regex, text))