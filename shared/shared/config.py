import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "dictionary.db"
CSV_PATH = DATA_DIR / "freq_list.csv"
TTS_OUTPUT_FOLDER = PROJECT_ROOT / "output"
ACCENTS_FILE = DATA_DIR / "accents.txt"

DATA_DIR.mkdir(exist_ok=True)
TTS_OUTPUT_FOLDER.mkdir(exist_ok=True)

DICT_URL = os.getenv("DICT_URL", "https://www.jardic.ru/search/search_r.php")
JARDIC_PATH = os.getenv(
    "JARDIC_PATH", r"C:\Program Files (x86)\JardicPro\JardicPro.exe"
)
TTS_BATCH_SIZE = int(os.getenv("TTS_BATCH_SIZE", "8"))
TTS_SPEAKER_ID = int(os.getenv("TTS_SPEAKER_ID", "13"))
VOICEVOX_URL = os.getenv("VOICEVOX_URL", "http://127.0.0.1:50021")
