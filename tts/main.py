import os
import requests
import io
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

VOICEVOX_URL = "http://127.0.0.1:50021"


def main():
    basicConfig(level=INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    words = get_words()

    words_to_process = [
        w for w in words if not os.path.exists(os.path.join(OUTPUT_DIR, f"{w[0]}.wav"))
    ]

    Logger.info(f"Осталось озвучить слов: {len(words_to_process)}")

    with requests.Session() as session:
        for i in range(0, len(words_to_process), BATCH_SIZE):
            batch = words_to_process[i : i + BATCH_SIZE]

            text_to_synth = "。".join([w[0] for w in batch]) + "。"

            try:
                query_res = session.post(
                    f"{VOICEVOX_URL}/audio_query",
                    params={"text": text_to_synth, "speaker": SPEAKER_ID},
                    timeout=15,
                )
                query_res.raise_for_status()
                query_data = query_res.json()

                query_data["speedScale"] = 0.8

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
                    for chunk, word_row in zip(chunks, batch):
                        w = word_row[0]
                        fn = os.path.join(OUTPUT_DIR, f"{w}.wav")
                        chunk.export(fn, format="wav")
                    Logger.info(
                        f"Батч {i // BATCH_SIZE + 1} успешно обработан ({len(batch)} слов)."
                    )
                else:
                    Logger.warning(
                        f"Несовпадение. Слов: {len(batch)}, аудио файлов: {len(chunks)}. Используем Fallback"
                    )
                    fallback_single_generation(batch, session)

            except Exception as e:
                Logger.error(
                    f"Ошибка при обработке батча (начиная с {batch[0][0]}): {e}"
                )


def fallback_single_generation(batch: list[list[str]], session):
    for word_row in batch:
        w = word_row[0]
        fn = os.path.join(OUTPUT_DIR, f"{w}.wav")
        try:
            q_res = session.post(
                f"{VOICEVOX_URL}/audio_query", params={"text": w, "speaker": SPEAKER_ID}
            )
            q_data = q_res.json()
            q_data["speedScale"] = 0.8

            s_res = session.post(
                f"{VOICEVOX_URL}/synthesis", params={"speaker": SPEAKER_ID}, json=q_data
            )

            with open(fn, "wb") as f:
                f.write(s_res.content)
            Logger.info(f"Fallback: обработано слово {w}")
        except Exception as e:
            Logger.error(f"Ошибка Fallback для {w}: {e}")


if __name__ == "__main__":
    main()
