import pykakasi

kks = pykakasi.kakasi()

def get_hiragana(input): 
    re = ''
    convert = kks.convert(input)
    for item in convert:
        re += item['hira']
    return re