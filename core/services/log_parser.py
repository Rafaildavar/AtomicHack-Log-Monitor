"""Парсер логов - логика коллеги адаптированная для sync/async использования.

Содержит точную логику парсинга из src/bot/services/log_parser.py
с поддержкой как синхронного (для API), так и асинхронного (для бота) режимов.
"""

import logging
import os
import re
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class LogParser:
    """Парсер логов для анализа аномалий.
    
    Логика написана коллегой, поддерживает синхронный и асинхронный режимы.
    """

    def __init__(self):
        """Инициализация парсера."""
        pass

    def parse_log_files(self, file_paths: List[str]) -> pd.DataFrame:
        """Парсит файлы логов в DataFrame (синхронная версия для API).

        Args:
            file_paths: Список путей к файлам логов

        Returns:
            DataFrame с распарсенными логами
        """
        all_logs = []

        logger.info(f"Начинаю парсинг {len(file_paths)} файлов")

        for file_path in file_paths:
            try:
                logger.info(f"Парсинг файла: {file_path}")

                # Читаем файл
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                except UnicodeDecodeError:
                    logger.warning(f"Ошибка кодировки файла {file_path}. Попробую другую кодировку.")
                    with open(file_path, 'r', encoding='latin-1') as file:
                        content = file.read()

                lines = content.splitlines()
                logger.info(f"Файл {Path(file_path).name} содержит {len(lines)} строк")

                parsed_lines = 0

                # Парсим строки (логика коллеги)
                for line_num, line in enumerate(lines, 1):
                    parsed = self._parse_log_line(line.strip())
                    if parsed:
                        parsed['filename'] = Path(file_path).name
                        parsed['line_number'] = line_num
                        parsed['full_line'] = line.strip()  # Сохраняем полную строку
                        all_logs.append(parsed)
                        parsed_lines += 1

                logger.info(f"В файле {Path(file_path).name} найдено {parsed_lines} валидных строк логов")

            except Exception as e:
                logger.warning(f"Ошибка при парсинге файла {file_path}: {e}")
                continue

        logger.info(f"Всего распарсено {len(all_logs)} строк логов из всех файлов")
        return pd.DataFrame(all_logs) if all_logs else pd.DataFrame()

    def extract_zip(self, zip_path: str, extract_dir: Optional[str] = None) -> List[str]:
        """Извлекает файлы из ZIP архива (синхронная версия для API).

        Args:
            zip_path: Путь к ZIP файлу
            extract_dir: Директория для извлечения (если None, создается временная)

        Returns:
            Список путей к извлеченным файлам
        """
        extracted_files = []

        if extract_dir is None:
            import tempfile
            extract_dir = tempfile.mkdtemp()

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                logger.info(f"Извлечение ZIP файла с {len(zip_ref.filelist)} файлами")

                for file_info in zip_ref.filelist:
                    logger.info(f"Проверка файла: {file_info.filename}")

                    # Извлекаем txt, log файлы и CSV файлы с аномалиями (логика коллеги)
                    if (file_info.filename.endswith('.txt') or
                        file_info.filename.endswith('.log') or
                        file_info.filename.endswith('anomalies_problems.csv')):
                        try:
                            # Извлекаем файл с сохранением структуры папок
                            extracted_path = zip_ref.extract(file_info, extract_dir)
                            extracted_files.append(extracted_path)
                            logger.info(f"Извлечен файл: {extracted_path}")
                        except Exception as e:
                            logger.warning(f"Ошибка извлечения файла {file_info.filename}: {e}")

            logger.info(f"Извлечено {len(extracted_files)} лог файлов")
            return extracted_files

        except Exception as e:
            logger.error(f"Ошибка извлечения ZIP файла: {e}")
            raise

    def _parse_log_line(self, line: str) -> Optional[Dict]:
        """Парсит строку лога (точная логика коллеги).

        Args:
            line: Строка лога

        Returns:
            Словарь с распарсенными данными или None
        """
        # Паттерн для формата: 2025-10-02T13:18:00 INFO hardware: Fan speed at 1592 RPM
        pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s+(\w+)\s+([^:]+):\s*(.+)$'
        match = re.match(pattern, line)

        if match:
            level = match.group(2).strip().upper()
            
            # Нормализуем уровень (убираем лишние символы и приводим к верхнему регистру)
            if 'WARNING' in level:
                level = 'WARNING'
            elif 'ERROR' in level:
                level = 'ERROR'
            
            return {
                'datetime': match.group(1),
                'level': level,
                'source': match.group(3),
                'text': match.group(4)
            }

        # Альтернативный паттерн для простых логов
        simple_pattern = r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\w+)\s+(.+)$'
        match = re.match(simple_pattern, line)

        if match:
            level = match.group(2).strip().upper()
            
            # Нормализуем уровень
            if 'WARNING' in level:
                level = 'WARNING'
            elif 'ERROR' in level:
                level = 'ERROR'
            
            return {
                'datetime': match.group(1),
                'level': level,
                'source': 'unknown',
                'text': match.group(3)
            }

        return None

    def analyze_logs_basic(self, df: pd.DataFrame) -> Dict:
        """Выполняет базовый анализ логов (логика коллеги).

        Args:
            df: DataFrame с логами

        Returns:
            Словарь со статистикой
        """
        if df.empty:
            return {
                'total_lines': 0,
                'error_count': 0,
                'warning_count': 0,
                'info_count': 0,
                'sources': [],
                'time_range': None,
                'top_messages': [],
                'level_distribution': {}
            }

        # Базовая статистика
        total_lines = len(df)
        error_count = len(df[df['level'].str.upper().isin(['ERROR', 'CRITICAL', 'FATAL'])])
        warning_count = len(df[df['level'].str.upper() == 'WARNING'])
        info_count = len(df[df['level'].str.upper() == 'INFO'])

        # Распределение по уровням
        level_distribution = df['level'].value_counts().to_dict()

        # Источники
        sources = df['source'].value_counts().head(10).to_dict()

        # Временной диапазон
        time_range = None
        if 'datetime' in df.columns:
            try:
                df['datetime'] = pd.to_datetime(df['datetime'])
                time_range = {
                    'start': df['datetime'].min().isoformat(),
                    'end': df['datetime'].max().isoformat()
                }
            except:
                pass

        # Топ сообщений
        top_messages = df['text'].value_counts().head(5).to_dict()

        return {
            'total_lines': total_lines,
            'error_count': error_count,
            'warning_count': warning_count,
            'info_count': info_count,
            'sources': sources,
            'time_range': time_range,
            'top_messages': top_messages,
            'level_distribution': level_distribution
        }

