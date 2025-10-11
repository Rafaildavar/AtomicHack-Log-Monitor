"""Простой сервис для анализа файлов и создания Excel отчетов."""

import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)


class SimpleFileAnalyzer:
    """Простой анализатор файлов для создания Excel отчетов."""

    def __init__(self):
        """Инициализация анализатора."""
        pass

    def analyze_file(self, file_path: str) -> dict:
        """Анализирует файл и возвращает статистику.

        Args:
            file_path: Путь к файлу

        Returns:
            Словарь со статистикой анализа
        """
        try:
            # Определяем тип файла
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.csv':
                return self._analyze_csv(file_path)
            elif file_extension in ['.txt', '.log']:
                return self._analyze_text(file_path)
            else:
                return self._analyze_generic(file_path)

        except Exception as e:
            logger.error(f"Ошибка анализа файла {file_path}: {e}")
            return {
                'file_name': os.path.basename(file_path),
                'file_type': 'unknown',
                'total_lines': 0,
                'error': str(e)
            }

    def _analyze_csv(self, file_path: str) -> dict:
        """Анализирует CSV файл."""
        try:
            df = pd.read_csv(file_path, sep=';')
            return {
                'file_name': os.path.basename(file_path),
                'file_type': 'csv',
                'total_lines': len(df),
                'columns': list(df.columns),
                'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
            }
        except Exception as e:
            return {
                'file_name': os.path.basename(file_path),
                'file_type': 'csv',
                'total_lines': 0,
                'error': str(e)
            }

    def _analyze_text(self, file_path: str) -> dict:
        """Анализирует текстовый файл."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Подсчет строк по уровням логирования
            error_count = sum(1 for line in lines if 'ERROR' in line.upper())
            warning_count = sum(1 for line in lines if 'WARNING' in line.upper())
            info_count = sum(1 for line in lines if 'INFO' in line.upper())

            # Определяем источники (простая эвристика)
            sources = {}
            for line in lines[:1000]:  # Анализируем первые 1000 строк
                if ':' in line:
                    source = line.split(':')[0].strip()
                    sources[source] = sources.get(source, 0) + 1

            return {
                'file_name': os.path.basename(file_path),
                'file_type': 'text',
                'total_lines': len(lines),
                'error_count': error_count,
                'warning_count': warning_count,
                'info_count': info_count,
                'top_sources': dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5])
            }
        except Exception as e:
            return {
                'file_name': os.path.basename(file_path),
                'file_type': 'text',
                'total_lines': 0,
                'error': str(e)
            }

    def _analyze_generic(self, file_path: str) -> dict:
        """Анализирует любой файл."""
        try:
            # Простая статистика файла
            file_size = os.path.getsize(file_path)
            with open(file_path, 'rb') as f:
                content = f.read()
                total_lines = content.count(b'\n')

            return {
                'file_name': os.path.basename(file_path),
                'file_type': 'binary',
                'total_lines': total_lines,
                'file_size': file_size
            }
        except Exception as e:
            return {
                'file_name': os.path.basename(file_path),
                'file_type': 'unknown',
                'error': str(e)
            }

    def create_excel_report(self, analysis_results: list, output_path: str = "reports/file_analysis.xlsx") -> str:
        """Создает Excel отчет из результатов анализа.

        Args:
            analysis_results: Список результатов анализа файлов
            output_path: Путь для сохранения Excel файла

        Returns:
            Путь к созданному файлу
        """
        try:
            # Создаем директорию если нужно
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Создаем DataFrame из результатов
            if not analysis_results:
                # Создаем пустой отчет
                report_data = [{
                    'Файл': 'Нет данных',
                    'Тип': 'Нет данных',
                    'Всего строк': 0,
                    'Статус': 'Анализ не выполнен'
                }]
            else:
                report_data = []
                for result in analysis_results:
                    if 'error' in result:
                        # Файл с ошибкой
                        report_data.append({
                            'Файл': result['file_name'],
                            'Тип': result.get('file_type', 'unknown'),
                            'Всего строк': result.get('total_lines', 0),
                            'Статус': f"Ошибка: {result['error']}"
                        })
                    elif 'results' in result and result['results']:
                        # ML анализ с результатами
                        base_info = {
                            'Файл': result['file_name'],
                            'Тип анализа': result.get('analysis_type', 'ml_anomaly_detection'),
                            'Всего сценариев': result.get('total_scenarios', 0),
                            'Всего проблем': result.get('total_problems', 0)
                        }
                        report_data.append(base_info)

                        # Добавляем детальные результаты аномалий
                        for anomaly in result['results']:
                            report_data.append({
                                'Сценарий': anomaly.get('Сценарий', ''),
                                'ID аномалии': anomaly.get('ID аномалии', ''),
                                'ID проблемы': anomaly.get('ID проблемы', ''),
                                'Файл с проблемой': anomaly.get('Файл с проблемой', ''),
                                '№ строки': anomaly.get('№ строки', ''),
                                'Строка из лога': anomaly.get('Строка из лога', ''),
                                'Уверенность': anomaly.get('Уверенность', ''),
                                'Аномалия': anomaly.get('Аномалия', ''),
                                'Статус': anomaly.get('Статус', '')
                            })
                    else:
                        # Обычный анализ файла
                        base_info = {
                            'Файл': result['file_name'],
                            'Тип': result.get('file_type', 'unknown'),
                            'Всего строк': result.get('total_lines', 0)
                        }

                        # Добавляем специфичную информацию
                        if result.get('file_type') == 'csv':
                            base_info['Колонки'] = ', '.join(result.get('columns', []))
                            base_info['Пример данных'] = str(result.get('sample_data', []))
                        elif result.get('file_type') == 'text':
                            base_info['Ошибок'] = result.get('error_count', 0)
                            base_info['Предупреждений'] = result.get('warning_count', 0)
                            base_info['Информационных'] = result.get('info_count', 0)

                        report_data.append(base_info)

            # Создаем DataFrame и сохраняем в Excel
            df = pd.DataFrame(report_data)
            df.to_excel(output_path, index=False, engine='openpyxl')

            logger.info(f"Excel отчет создан: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Ошибка создания Excel отчета: {e}")
            return ""
