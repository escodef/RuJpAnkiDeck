import os
import csv

from typing import List

csv_name = os.getenv("CSV_FILE")

filter = ["助動詞", "記号", "動詞-接尾", "助詞"]


def get_words() -> List[List[str]]:
    words = []
    with open(csv_name, "r", newline="", encoding="utf-8") as f:
        csv_file = csv.reader(f)
        for row in csv_file:
            if row[1] in filter or "【" in row[0]:
                continue
            words.append(row)
        return words
