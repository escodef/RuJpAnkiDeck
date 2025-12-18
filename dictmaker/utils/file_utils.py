import json
from models.models import DictionaryList

def save_dictionary(dictionary: DictionaryList, filepath: str):
    """Сохраняет список переводов в JSON файл"""
    data = [translation.model_dump(mode='python') for translation in dictionary]

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
