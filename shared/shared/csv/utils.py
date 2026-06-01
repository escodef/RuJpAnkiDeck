import os
import csv

from typing import List

CSV_PATH = os.getenv("CSV_FILE", "./data/freq_list.csv")

EXCLUDED_POS = frozenset(["助動詞", "記号", "動詞-接尾", "助詞"])


def get_words() -> List[List[str]]:
    words = []
    line_number = 0

    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        csv_file = csv.reader(f)
        print(f"Открытие файла: {CSV_PATH}")

        try:
            for row in csv_file:
                line_number += 1
                if row[1] in EXCLUDED_POS or "【" in row[0]:
                    continue
                words.append(row)
        except csv.Error as e:
            print(f"Ошибка в строке №{line_number}")
            print(f"Тип ошибки: {e}")
            raise

        return words
