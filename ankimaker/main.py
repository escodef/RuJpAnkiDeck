import os
import json
from anki.collection import Collection
from anki.exporting import AnkiPackageExporter
from dotenv import load_dotenv

load_dotenv()

json_dict = os.getenv("DICT_JSON_OUTPUT")

with open(json_dict, 'r', encoding='utf-8') as f:
    data = json.load(f)

temp_db = "temp_col.anki2"
if os.path.exists(temp_db):
    os.remove(temp_db)

col = Collection(temp_db)

model = col.models.new("Japanese_Model")
col.models.add_field(model, col.models.new_field("Word"))
col.models.add_field(model, col.models.new_field("Reading"))
col.models.add_field(model, col.models.new_field("MainSense"))
col.models.add_field(model, col.models.new_field("Senses"))

model['css'] = """
.card {
    font-family: "Segoe UI", "Helvetica", sans-serif;
    font-size: 22px;
    text-align: center;
    color: #e0e0e0;
    background-color: #2c2c2c;
}

.nightMode .card {
    background-color: #1a1a1a;
    color: #ffffff;
}

.jp { 
    font-size: 45px; 
    font-weight: bold; 
    color: #64b5f6; 
    margin-top: 10px;
}

.reading { 
    font-size: 22px; 
    color: #b0bec5; 
    margin-bottom: 10px; 
}

.meaning { 
    font-size: 28px; 
    font-weight: bold; 
    color: #81c784; 
}

.extra { 
    font-size: 18px; 
    color: #90a4ae; 
    font-style: italic; 
    margin-top: 15px; 
}

hr { 
    border: none; 
    border-top: 1px solid #444; 
    margin: 20px 0; 
}
"""

t1 = col.models.new_template("JP -> RU")
t1['qfmt'] = '<div class="jp">{{Word}}</div>'
t1['afmt'] = """{{FrontSide}}<hr>
<div class="reading">{{Reading}}</div>
<div class="meaning">{{MainSense}}</div>
<div class="extra">{{Senses}}</div>"""
col.models.add_template(model, t1)

t2 = col.models.new_template("RU -> JP")
t2['qfmt'] = '<div class="meaning">{{MainSense}}</div>'
t2['afmt'] = """{{FrontSide}}<hr>
<div class="jp">{{Word}}</div>
<div class="reading">{{Reading}}</div>
<div class="extra">{{Senses}}</div>"""
col.models.add_template(model, t2)
col.models.add(model)

deck_id_jp = col.decks.id("Слова::Японский -> Русский")
deck_id_ru = col.decks.id("Слова::Русский -> Японский")

for item in data:
    word = item['word'].strip()

    reading = item['reading'].replace('\r\n', '<br>').replace('\n', '<br>').strip()
    mainsense = item['mainsense'].replace('\r\n', '<br>').replace('\n', '<br>').strip()
    senses = item['senses'].replace('\r\n', '<br>').replace('\n', '<br>').strip()
    
    note = col.new_note(model)
    note['Word'] = word
    note['Reading'] = reading
    note['MainSense'] = mainsense
    note['Senses'] = senses
    col.add_note(note, deck_id_jp)

    cards = note.cards()
    card_ru = cards[1]
    card_ru.did = deck_id_ru
    
    col.update_card(card_ru)

exporter = AnkiPackageExporter(col)
output_file = "japanese_vocab.apkg"
exporter.exportInto(output_file)

col.close()
if os.path.exists(temp_db):
    os.remove(temp_db)
if os.path.exists(temp_db + ".log"):
    os.remove(temp_db + ".log")

print(f"Готово! Файл создан: {output_file}")