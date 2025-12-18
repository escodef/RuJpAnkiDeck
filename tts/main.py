import csv
import os
from logging import getLogger, basicConfig, INFO
from kokoro import KPipeline
import soundfile as sf
from dotenv import load_dotenv

load_dotenv()
Logger = getLogger(__name__)

filter = ["助動詞", "記号", "動詞-接尾"]
output = 'temp'
csv_name = os.getenv("CSV_FILE")

def main():
    basicConfig(level=INFO)

    if not os.path.exists(output):
        os.mkdir(output)

    pipeline = KPipeline(lang_code="j")
    words = get_words()

    for word in words[:10]:
        reading = word[2]
        w = word[0]
        fn = os.path.join(output, f"{w}.wav")
        if os.path.exists(fn):
            continue

        try:
            generator = pipeline(reading, voice="jf_alpha", speed=0.8)
            for _, _, audio in generator:
                sf.write(fn, audio, 24000)
        except Exception as e:
            Logger.error(f"Error processing {w}: {e}")

def get_words() -> list[list[str]]:
    a = []
    with open(csv_name, 'r', newline='') as f:
        csv_file = csv.reader(f)
        for row in csv_file:
            if row[1] in filter:
                continue
            a.append(row)
        return a

if __name__ == "__main__":
    main()
