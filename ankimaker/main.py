import os
import sys
import logging

from anki.collection import Collection
from anki.exporting import AnkiPackageExporter
from template import CARD_CSS, JP_RU_FRONT, JP_RU_BACK, RU_JP_FRONT, RU_JP_BACK
from dotenv import load_dotenv

load_dotenv()

tts_folder = os.getenv("TTS_OUTPUT_FOLDER")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database.db_session import init_db
from shared.database.utils import get_by_reading
from shared.csv.utils import get_words

init_db()

temp_db = "temp_col.anki2"
if os.path.exists(temp_db):
    os.remove(temp_db)

col = Collection(temp_db)

model = col.models.new("Japanese_Model")
col.models.add_field(model, col.models.new_field("Word"))
col.models.add_field(model, col.models.new_field("Reading"))
col.models.add_field(model, col.models.new_field("MainSense"))
col.models.add_field(model, col.models.new_field("Senses"))

model['css'] = CARD_CSS

t1 = col.models.new_template("JP -> RU")
t1['qfmt'] = JP_RU_FRONT
t1['afmt'] = JP_RU_BACK
col.models.add_template(model, t1)

t2 = col.models.new_template("RU -> JP")
t2['qfmt'] = RU_JP_FRONT
t2['afmt'] = RU_JP_BACK
col.models.add_template(model, t2)
col.models.add(model)

words_to_parse = get_words()

for index, item in enumerate(words_to_parse[:100]):
    start_range = (index // 5000) * 5
    end_range = start_range + 5
    range_str = f"{start_range:02d}-{end_range:02d}k"
    
    current_deck_id_jp = col.decks.id(f"Слова::Японский - Русский::{range_str}")
    current_deck_id_ru = col.decks.id(f"Слова::Русский - Японский::{range_str}")

    word = item[0]
    translations = get_by_reading(word)
    if not translations:
        logging.warning(f'translations not found for {word}')
        continue

    for translation in translations:

        word_val = translation.word.strip()
        reading = translation.reading.replace('\r\n', '<br>').replace('\n', '<br>').strip()
        mainsense = translation.mainsense.replace('\r\n', '<br>').replace('\n', '<br>').strip()
        senses = translation.senses.replace('\r\n', '<br>').replace('\n', '<br>').strip()
        
        note = col.new_note(model)
        note['Word'] = word_val
        note['Reading'] = reading
        note['MainSense'] = mainsense
        note['Senses'] = senses

        # audio_filename = f"{word_val}.wav"
        # audio_path = os.path.join(tts_folder, audio_filename)

        # if os.path.exists(audio_path):
        #     col.media.add_file(audio_path)
        #     note['Reading'] += f" [sound:{audio_filename}]"

        col.add_note(note, current_deck_id_jp)

        cards = note.cards()
        if len(cards) > 1:
            card_ru = cards[1]
            card_ru.did = current_deck_id_ru
            col.update_card(card_ru)
        if index % 1000 == 0:
            col.save()

exporter = AnkiPackageExporter(col)
output_file = "japanese_vocab.apkg"
exporter.exportInto(output_file)

col.close()
if os.path.exists(temp_db):
    os.remove(temp_db)
if os.path.exists(temp_db + ".log"):
    os.remove(temp_db + ".log")

print(f"Готово! Файл создан: {output_file}")