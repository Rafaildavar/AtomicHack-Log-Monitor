"""Сервис для хранения истории анализа логов."""

import json
import os
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict


@dataclass
class AnalysisRecord:
    """Запись анализа логов."""
    user_id: int
    file_name: str
    timestamp: str
    total_lines: int
    error_count: int
    warning_count: int
    info_count: int
    sources: Dict[str, int]
    top_messages: Dict[str, int]
    level_distribution: Dict[str, int]


class AnalysisHistory:
    """Сервис для управления историей анализа."""

    def __init__(self, storage_file: str = "data/analysis_history.json"):
        self.storage_file = storage_file
        self._ensure_storage_dir()
        self._history: List[AnalysisRecord] = []
        self._load_history()

    def _ensure_storage_dir(self):
        """Создает директорию для хранения данных если она не существует."""
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)

    def _load_history(self):
        """Загружает историю из файла."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._history = [
                        AnalysisRecord(
                            user_id=record['user_id'],
                            file_name=record['file_name'],
                            timestamp=record['timestamp'],
                            total_lines=record['total_lines'],
                            error_count=record['error_count'],
                            warning_count=record['warning_count'],
                            sources=record['sources'],
                            top_errors=record['top_errors']
                        ) for record in data
                    ]
            except Exception:
                self._history = []

    def _save_history(self):
        """Сохраняет историю в файл."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(record) for record in self._history], f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def add_record(self, user_id: int, analysis: Dict, file_name: str):
        """Добавляет новую запись анализа."""
        record = AnalysisRecord(
            user_id=user_id,
            file_name=file_name,
            timestamp=datetime.now().isoformat(),
            total_lines=analysis.get('total_lines', 0),
            error_count=analysis.get('error_count', 0),
            warning_count=analysis.get('warning_count', 0),
            info_count=analysis.get('info_count', 0),
            sources=analysis.get('sources', {}),
            top_messages=analysis.get('top_messages', {}),
            level_distribution=analysis.get('level_distribution', {})
        )

        self._history.append(record)
        self._save_history()

    def get_user_history(self, user_id: int, limit: int = 10) -> List[AnalysisRecord]:
        """Получает историю анализа для пользователя."""
        user_records = [r for r in self._history if r.user_id == user_id]
        return user_records[-limit:] if user_records else []

    def get_statistics(self, user_id: int = None) -> Dict:
        """Получает статистику по анализам."""
        if user_id:
            records = [r for r in self._history if r.user_id == user_id]
        else:
            records = self._history

        if not records:
            return {
                'total_analyses': 0,
                'total_errors': 0,
                'total_warnings': 0,
                'avg_errors_per_analysis': 0,
                'most_common_sources': {},
                'most_common_errors': {}
            }

        total_analyses = len(records)
        total_errors = sum(r.error_count for r in records)
        total_warnings = sum(r.warning_count for r in records)

        # Собираем статистику по источникам
        all_sources = {}
        for record in records:
            for source, count in record.sources.items():
                all_sources[source] = all_sources.get(source, 0) + count

        # Собираем статистику по ошибкам
        all_errors = {}
        for record in records:
            for error, count in record.top_errors.items():
                all_errors[error] = all_errors.get(error, 0) + count

        # Сортируем и берем топ
        most_common_sources = dict(sorted(all_sources.items(), key=lambda x: x[1], reverse=True)[:5])
        most_common_errors = dict(sorted(all_errors.items(), key=lambda x: x[1], reverse=True)[:5])

        return {
            'total_analyses': total_analyses,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'avg_errors_per_analysis': round(total_errors / total_analyses, 2) if total_analyses > 0 else 0,
            'most_common_sources': most_common_sources,
            'most_common_errors': most_common_errors
        }
