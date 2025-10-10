import pandas as pd
from pathlib import Path
import re


def parse_log_line(line: str):
    """Парсит строку лога и возвращает словарь с атрибутами"""
    pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s+(\w+)\s+([^:]+):\s*(.+)$'
    match = re.match(pattern, line.strip())

    if match:
        return {
            'datetime': match.group(1),
            'level': match.group(2),
            'source': match.group(3),
            'text': match.group(4)
        }
    return None


def logs_to_dataframe(folder_path: str) -> pd.DataFrame:
    """Читает все txt файлы из папки и создает DataFrame со строками, содержащими WARNING или ERROR"""
    folder = Path(folder_path)
    all_logs = []

    for file_path in folder.glob("*.txt"):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    if 'WARNING' in line or 'ERROR' in line:
                        parsed = parse_log_line(line)
                        if parsed:
                            parsed['filename'] = file_path.name
                            parsed['line_number'] = line_num
                            all_logs.append(parsed)
        except:
            continue

    return pd.DataFrame(all_logs) if all_logs else pd.DataFrame()


if __name__ == "__main__":
    df = logs_to_dataframe("Validation Cases/ValidationCase 1")
    print(df.head())