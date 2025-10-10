"""Управление временными файлами и директориями."""

import os
import tempfile
import shutil
from typing import List


class TempFileManager:
    """Менеджер для создания и очистки временных файлов."""

    def __init__(self):
        self.temp_files: List[str] = []
        self.temp_dirs: List[str] = []

    def create_temp_file(self, suffix: str = '') -> str:
        """Создает временный файл и возвращает его путь."""
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        self.temp_files.append(path)
        return path

    def create_temp_dir(self) -> str:
        """Создает временную директорию и возвращает ее путь."""
        path = tempfile.mkdtemp()
        self.temp_dirs.append(path)
        return path

    def cleanup(self):
        """Удаляет все созданные временные файлы и директории."""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass

        for dir_path in self.temp_dirs:
            try:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
            except Exception:
                pass

        self.temp_files.clear()
        self.temp_dirs.clear()
