#!/usr/bin/env python3
"""
Скрипт для прямого анализа Test Cases через ML модуль
Выводит результаты в CSV формате без использования Telegram
"""

import os
import sys
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

# Добавляем src в путь для импорта модулей
sys.path.insert(0, str(Path(__file__).parent))

from src.bot.services.ml_log_analyzer import MLLogAnalyzer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_log_file(file_path: str, scenario_name: str) -> list:
    """
    Парсит файл логов и возвращает список записей
    
    Args:
        file_path: путь к файлу логов
        scenario_name: имя сценария
    
    Returns:
        список словарей с распарсенными логами
    """
    logs = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                
                # Парсинг формата: "дата время уровень источник: текст"
                parts = line_stripped.split(maxsplit=2)
                if len(parts) < 3:
                    continue
                
                dt, level, rest = parts[0], parts[1], parts[2]
                
                # Нормализация уровня
                level = level.strip().upper()
                if 'WARNING' in level:
                    level = 'WARNING'
                elif 'ERROR' in level:
                    level = 'ERROR'
                else:
                    continue  # Пропускаем не WARNING/ERROR
                
                # Разделение source и text
                if ':' in rest:
                    source_parts = rest.split(':', 1)
                    source = source_parts[0].strip()
                    text = source_parts[1].strip()
                else:
                    source = 'unknown'
                    text = rest
                
                logs.append({
                    'datetime': dt,
                    'level': level,
                    'source': source,
                    'text': text,
                    'full_line': line_stripped,
                    'filename': os.path.basename(file_path),
                    'line_number': line_num
                })
    
    except Exception as e:
        logger.error(f"Ошибка при парсинге файла {file_path}: {e}")
    
    return logs


def analyze_test_case(test_case_dir: str, ml_analyzer: MLLogAnalyzer, scenario_id: int) -> pd.DataFrame:
    """
    Анализирует один тест-кейс
    
    Args:
        test_case_dir: путь к директории тест-кейса
        ml_analyzer: экземпляр ML анализатора
        scenario_id: ID сценария
    
    Returns:
        DataFrame с результатами анализа
    """
    test_case_name = os.path.basename(test_case_dir)
    logger.info(f"Анализ {test_case_name}...")
    
    # Поиск локального словаря аномалий в папке тест-кейса
    anomalies_file = os.path.join(test_case_dir, 'anomalies_problems.csv')
    if not os.path.exists(anomalies_file):
        logger.warning(f"Файл anomalies_problems.csv не найден в {test_case_name}")
        return pd.DataFrame()
    
    # Парсинг всех .txt файлов
    all_logs = []
    for file in os.listdir(test_case_dir):
        if file.endswith('.txt'):
            file_path = os.path.join(test_case_dir, file)
            logs = parse_log_file(file_path, test_case_name)
            all_logs.extend(logs)
    
    if not all_logs:
        logger.warning(f"Не найдено WARNING/ERROR логов в {test_case_name}")
        return pd.DataFrame()
    
    # Создание DataFrame из логов
    logs_df = pd.DataFrame(all_logs)
    logger.info(f"  Найдено {len(logs_df)} WARNING/ERROR записей")
    
    # Загрузка словаря аномалий из CSV (с разделителем ';')
    try:
        anomalies_df = pd.read_csv(anomalies_file, sep=';', encoding='utf-8')
    except:
        try:
            anomalies_df = pd.read_csv(anomalies_file, sep=';', encoding='windows-1251')
        except Exception as e:
            logger.error(f"Ошибка загрузки {anomalies_file}: {e}")
            return pd.DataFrame()
    
    # ML анализ
    try:
        results_df = ml_analyzer.analyze_logs_with_ml(logs_df, anomalies_df)
        
        if not results_df.empty:
            # Добавляем ID сценария
            results_df.insert(0, 'ID сценария', scenario_id)
            logger.info(f"  ✅ Найдено {len(results_df)} проблем")
            return results_df
        else:
            logger.info(f"  ℹ️  Проблем не найдено")
            return pd.DataFrame()
    
    except Exception as e:
        logger.error(f"Ошибка при ML анализе {test_case_name}: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def main():
    """Основная функция для анализа всех Test Cases"""
    
    # Путь к директории Test Cases
    test_cases_dir = Path(__file__).parent / "Test Cases"
    
    if not test_cases_dir.exists():
        logger.error(f"Директория {test_cases_dir} не найдена!")
        return
    
    # Инициализация ML анализатора
    logger.info("Инициализация ML модели...")
    ml_analyzer = MLLogAnalyzer()
    
    # Получение всех тест-кейсов и сортировка
    test_cases = sorted([
        d for d in test_cases_dir.iterdir() 
        if d.is_dir() and d.name.startswith('TestCase')
    ], key=lambda x: int(x.name.replace('TestCase ', '').strip()))
    
    logger.info(f"Найдено {len(test_cases)} тест-кейсов")
    
    # Анализ всех тест-кейсов
    all_results = []
    
    for idx, test_case_path in enumerate(test_cases, 1):
        result_df = analyze_test_case(str(test_case_path), ml_analyzer, idx)
        if not result_df.empty:
            all_results.append(result_df)
    
    # Объединение всех результатов
    if all_results:
        final_df = pd.concat(all_results, ignore_index=True)
        
        # Преобразование числовых колонок в целые числа
        final_df['ID аномалии'] = final_df['ID аномалии'].astype('Int64')  # Int64 поддерживает NaN
        final_df['ID проблемы'] = final_df['ID проблемы'].astype('Int64')
        final_df['№ строки'] = final_df['№ строки'].astype('Int64')
        
        # Удаление строк где все значения NaN (пустые строки)
        final_df = final_df.dropna(how='all')
        
        # Заполнение NaN значений нулями для корректной обработки на сервере
        # (хотя после наших изменений не должно быть NaN)
        final_df['ID аномалии'] = final_df['ID аномалии'].fillna(0).astype(int)
        final_df['ID проблемы'] = final_df['ID проблемы'].fillna(0).astype(int)
        final_df['№ строки'] = final_df['№ строки'].fillna(0).astype(int)
        
        # Сохранение в CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"test_cases_results_{timestamp}.csv"
        final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ АНАЛИЗ ЗАВЕРШЕН")
        logger.info(f"{'='*60}")
        logger.info(f"Обработано тест-кейсов: {len(test_cases)}")
        logger.info(f"Найдено проблем: {len(final_df)}")
        logger.info(f"Уникальных аномалий: {final_df['ID аномалии'].nunique()}")
        logger.info(f"Уникальных проблем: {final_df['ID проблемы'].nunique()}")
        logger.info(f"\nРезультаты сохранены в: {output_file}")
        logger.info(f"{'='*60}\n")
        
        # Вывод первых 10 строк для проверки
        print("\nПример результатов (первые 10 строк):")
        print(final_df.head(10).to_string(index=False))
        
    else:
        logger.warning("Не найдено ни одной проблемы во всех тест-кейсах!")


if __name__ == "__main__":
    main()

