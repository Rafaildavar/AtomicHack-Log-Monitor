"""Сервис для парсинга и анализа логов."""

import asyncio
import logging
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from aiogram.types import Document

from ..utils.temp_manager import TempFileManager

logger = logging.getLogger(__name__)


class LogParser:
    """Парсер логов для анализа аномалий."""

    def __init__(self):
        self.temp_manager = TempFileManager()

    async def process_uploaded_file(self, document: Document, bot) -> Dict:
        """Обрабатывает загруженный файл с логами.

        Args:
            document: Документ из Telegram
            bot: Экземпляр бота для скачивания файлов

        Returns:
            Словарь с результатами анализа
        """
        try:
            logger.info(f"Начинаю обработку файла: {document.file_name}")

            # Скачиваем файл
            file_path = await self._download_file(document, bot)
            logger.info(f"Файл скачан: {file_path}")

            # Определяем тип файла и извлекаем логи
            if file_path.endswith('.zip'):
                logger.info("Обработка ZIP файла")
                log_files = await self._extract_zip(file_path)
                logger.info(f"Извлечено {len(log_files)} файлов")
            else:
                log_files = [file_path]
                logger.info("Обработка одиночного файла")

            # Парсим логи в DataFrame
            df = await self._parse_logs_to_dataframe(log_files)

            # Выполняем базовый анализ
            analysis = self._analyze_logs(df)
            logger.info(f"Анализ завершен: {analysis['total_lines']} строк, {analysis['error_count']} ошибок")

            # Очищаем временные файлы
            self.temp_manager.cleanup()

            return {
                'success': True,
                'analysis': analysis,
                'dataframe': df.to_dict('records') if not df.empty else []
            }

        except Exception as e:
            logger.error(f"Ошибка при обработке файла: {e}")
            # Очищаем временные файлы в случае ошибки
            self.temp_manager.cleanup()
            return {
                'success': False,
                'error': str(e)
            }

    async def _download_file(self, document: Document, bot) -> str:
        """Скачивает файл из Telegram."""
        import aiofiles

        file_info = await bot.get_file(document.file_id)

        # Создаем временный файл
        temp_file = self.temp_manager.create_temp_file(suffix=Path(document.file_name).suffix)

        # Скачиваем файл
        await bot.download_file(file_info.file_path, temp_file)

        return temp_file

    async def _extract_zip(self, zip_path: str) -> List[str]:
        """Извлекает файлы из ZIP архива."""
        extracted_files = []
        extract_dir = self.temp_manager.create_temp_dir()

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                logger.info(f"Извлечение ZIP файла с {len(zip_ref.filelist)} файлами")

                for file_info in zip_ref.filelist:
                    logger.info(f"Проверка файла: {file_info.filename}")

                    # Проверяем что файл является txt или log
                    if file_info.filename.endswith('.txt') or file_info.filename.endswith('.log'):
                        try:
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

    async def _parse_logs_to_dataframe(self, log_files: List[str]) -> pd.DataFrame:
        """Парсит файлы логов в DataFrame."""
        import aiofiles
        all_logs = []

        logger.info(f"Начинаю парсинг {len(log_files)} файлов")

        for file_path in log_files:
            try:
                logger.info(f"Парсинг файла: {file_path}")

                # Читаем файл асинхронно
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                    content = await file.read()

                lines = content.splitlines()
                logger.info(f"Файл {Path(file_path).name} содержит {len(lines)} строк")

                parsed_lines = 0

                # Парсим строки
                for line_num, line in enumerate(lines, 1):
                    parsed = self._parse_log_line(line.strip())
                    if parsed:
                        parsed['filename'] = Path(file_path).name
                        parsed['line_number'] = line_num
                        all_logs.append(parsed)
                        parsed_lines += 1

                logger.info(f"В файле {Path(file_path).name} найдено {parsed_lines} валидных строк логов")

            except UnicodeDecodeError as e:
                logger.warning(f"Ошибка кодировки файла {file_path}: {e}. Попробую другую кодировку.")
                try:
                    # Попробуем прочитать с другой кодировкой
                    async with aiofiles.open(file_path, 'r', encoding='latin-1') as file:
                        content = await file.read()

                    lines = content.splitlines()
                    for line_num, line in enumerate(lines, 1):
                        parsed = self._parse_log_line(line.strip())
                        if parsed:
                            parsed['filename'] = Path(file_path).name
                            parsed['line_number'] = line_num
                            all_logs.append(parsed)
                except Exception as e2:
                    logger.warning(f"Ошибка при парсинге файла {file_path} даже с другой кодировкой: {e2}")
                    continue

            except Exception as e:
                logger.warning(f"Ошибка при парсинге файла {file_path}: {e}")
                continue

        logger.info(f"Всего распарсено {len(all_logs)} строк логов из всех файлов")
        return pd.DataFrame(all_logs) if all_logs else pd.DataFrame()

    def _parse_log_line(self, line: str) -> Dict | None:
        """Парсит строку лога."""
        import re

        # Паттерн для формата: 2025-10-02T13:18:00 INFO hardware: Fan speed at 1592 RPM
        pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s+(\w+)\s+([^:]+):\s*(.+)$'
        match = re.match(pattern, line)

        if match:
            return {
                'datetime': match.group(1),
                'level': match.group(2),
                'source': match.group(3),
                'text': match.group(4)
            }

        # Альтернативный паттерн для простых логов
        simple_pattern = r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\w+)\s+(.+)$'
        match = re.match(simple_pattern, line)

        if match:
            return {
                'datetime': match.group(1),
                'level': match.group(2),
                'source': 'unknown',
                'text': match.group(3)
            }

        return None

    def _analyze_logs(self, df: pd.DataFrame) -> Dict:
        """Выполняет базовый анализ логов."""
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

        # Топ сообщений (не только ошибки)
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
