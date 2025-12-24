import os
from logging import getLogger, basicConfig, INFO
from kokoro import KPipeline
import soundfile as sf
from dotenv import load_dotenv
from shared.csv.utils import get_words

load_dotenv()
Logger = getLogger(__name__)

output = 'temp'

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

if __name__ == "__main__":
    main()
