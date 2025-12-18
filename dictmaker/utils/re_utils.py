import re 

def has_cyrillic(text):
    return bool(re.search('[\u0400-\u04FF]', text))