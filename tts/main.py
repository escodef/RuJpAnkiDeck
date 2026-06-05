import os
import re
import requests
import io
import jaconv
from logging import getLogger, basicConfig, INFO
from dotenv import load_dotenv

from pydub import AudioSegment
from pydub.silence import split_on_silence

from shared.csv.utils import get_words

load_dotenv()

Logger = getLogger(__name__)

OUTPUT_DIR = os.getenv("TTS_OUTPUT_FOLDER", "output")
BATCH_SIZE = int(os.getenv("TTS_BATCH_SIZE", 8))
SPEAKER_ID = int(os.getenv("TTS_SPEAKER_ID", 13))
ACCENTS_FILE = os.getenv("TTS_ACCENTS_FILE", "../data/accents.txt")

VOICEVOX_URL = "http://127.0.0.1:50021"


def load_accents(filepath: str) -> dict:
    accents = {}
    if not os.path.exists(filepath):
        Logger.warning(
            f"Файл {filepath} не найден. Ударения будут расставлены по умолчанию."
        )
        return accents

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                kanji = parts[0]
                hira = parts[1]
                accent_str = parts[2]

                try:
                    accent = int(accent_str.split(",")[0])
                    accents[(kanji, hira)] = accent
                except ValueError:
                    pass
    return accents


def build_aquestalk_kana(katakana: str, accent: int) -> str:
    moras = re.findall(r"[ァ-ヴー][ァ-ォャ-ョヮ]*", katakana)

    if not moras:
        return katakana

    if accent == 0 or accent >= len(moras):
        return katakana + "'"

    moras.insert(accent, "'")
    return "".join(moras)


def main():
    basicConfig(level=INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    accents_dict = load_accents(ACCENTS_FILE)
    words = get_words()[:25000]

    words_to_process = []
    for w in words:
        kanji = w[0]
        katakana = w[2].strip()
        safe_katakana = katakana.replace("/", "").replace(" ", "")
        filename = f"{kanji}_{safe_katakana}.mp3"

        if not os.path.exists(os.path.join(OUTPUT_DIR, filename)):
            words_to_process.append((kanji, katakana, filename))

    Logger.info(f"Осталось озвучить слов: {len(words_to_process)}")

    with requests.Session() as session:
        for i in range(0, len(words_to_process), BATCH_SIZE):
            batch = words_to_process[i : i + BATCH_SIZE]

            aquestalk_phrases = []

            for kanji, katakana, filename in batch:
                hira = jaconv.kata2hira(katakana)
                accent = accents_dict.get((kanji, hira), 0)
                aq_str = build_aquestalk_kana(katakana, accent)
                aquestalk_phrases.append(aq_str)

            batch_text = "、".join(aquestalk_phrases)

            try:
                res_phrases = session.post(
                    f"{VOICEVOX_URL}/accent_phrases",
                    params={"text": batch_text, "is_kana": True, "speaker": SPEAKER_ID},
                    timeout=15,
                )
                res_phrases.raise_for_status()
                phrases_data = res_phrases.json()

                query_res = session.post(
                    f"{VOICEVOX_URL}/audio_query",
                    params={"text": "あ", "speaker": SPEAKER_ID},
                    timeout=15,
                )
                query_res.raise_for_status()
                query_data = query_res.json()

                query_data["accent_phrases"] = phrases_data
                query_data["speedScale"] = 0.8
                query_data["pauseLength"] = 0.8

                synth_res = session.post(
                    f"{VOICEVOX_URL}/synthesis",
                    params={"speaker": SPEAKER_ID},
                    json=query_data,
                    timeout=60,
                )
                synth_res.raise_for_status()

                audio = AudioSegment.from_file(
                    io.BytesIO(synth_res.content), format="wav"
                )

                chunks = split_on_silence(
                    audio,
                    min_silence_len=250,
                    silence_thresh=audio.dBFS - 30,
                    keep_silence=150,
                )

                if len(chunks) == len(batch):
                    for chunk, (kanji, katakana, filename) in zip(chunks, batch):
                        filename_mp3 = filename.rsplit(".", 1)[0] + ".mp3"
                        fn = os.path.join(OUTPUT_DIR, filename_mp3)
                        chunk.export(fn, format="mp3", bitrate="64k")
                    Logger.info(
                        f"Батч {i // BATCH_SIZE + 1} успешно обработан ({len(batch)} слов)."
                    )
                else:
                    Logger.warning(
                        f"Несовпадение. Слов: {len(batch)}, аудио файлов: {len(chunks)}. Используем Fallback"
                    )
                    fallback_single_generation(batch, session, accents_dict)

            except Exception as e:
                Logger.error(
                    f"Ошибка при обработке батча (начиная с {batch[0][0]}): {e}"
                )


def fallback_single_generation(batch: list[tuple], session, accents_dict):
    for kanji, katakana, filename in batch:
        hira = jaconv.kata2hira(katakana)
        accent = accents_dict.get((kanji, hira), 0)
        aq_str = build_aquestalk_kana(katakana, accent)

        try:
            res_phrases = session.post(
                f"{VOICEVOX_URL}/accent_phrases",
                params={"text": aq_str, "is_kana": True, "speaker": SPEAKER_ID},
            )
            res_phrases.raise_for_status()

            query_res = session.post(
                f"{VOICEVOX_URL}/audio_query",
                params={"text": "あ", "speaker": SPEAKER_ID},
            )
            query_data = query_res.json()
            query_data["accent_phrases"] = res_phrases.json()
            query_data["speedScale"] = 0.8
            query_data["prePhonemeLength"] = 0.15
            query_data["postPhonemeLength"] = 0.15

            synth_res = session.post(
                f"{VOICEVOX_URL}/synthesis",
                params={"speaker": SPEAKER_ID},
                json=query_data,
                timeout=30,
            )

            audio = AudioSegment.from_file(io.BytesIO(synth_res.content), format="wav")
            filename_mp3 = filename.rsplit(".", 1)[0] + ".mp3"

            fn = os.path.join(OUTPUT_DIR, filename_mp3)
            audio.export(fn, format="mp3", bitrate="64k")
            Logger.info(f"Fallback: успешно обработано {filename}")

        except Exception as e:
            Logger.error(f"Ошибка Fallback для {filename}: {e}")


if __name__ == "__main__":
    main()
