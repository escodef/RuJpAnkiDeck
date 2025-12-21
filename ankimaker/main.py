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

t1 = col.models.new_template("JP -> RU")
t1['qfmt'] = "{{Word}}"
t1['afmt'] = "{{FrontSide}}<hr>{{Reading}}<br>{{MainSense}}<br><i>{{Senses}}</i>"
col.models.add_template(model, t1)

t2 = col.models.new_template("RU -> JP")
t2['qfmt'] = "{{MainSense}}"
t2['afmt'] = "{{FrontSide}}<hr>{{Word}}<br>{{Reading}}<br><i>{{Senses}}</i>"
col.models.add_template(model, t2)

col.models.add(model)

deck_id_jp = col.decks.id("Japanese::JP_to_RU")
deck_id_ru = col.decks.id("Japanese::RU_to_JP")

for item in data:
    word = item['word'].strip()
    
    note = col.new_note(model)
    note['Word'] = word
    note['Reading'] = item['reading']
    note['MainSense'] = item['mainsense']
    note['Senses'] = item['senses']
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