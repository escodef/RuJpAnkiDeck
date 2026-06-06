def get_audio_filename(word: str, reading_katakana: str) -> str:
    safe_katakana = reading_katakana.strip().replace("/", "").replace(" ", "")
    return f"{word}_{safe_katakana}.mp3"
