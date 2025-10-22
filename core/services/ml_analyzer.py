"""ML анализатор логов - логика коллеги без изменений.

Этот модуль содержит точную копию логики из src/bot/services/ml_log_analyzer.py
для использования как в боте, так и в API.
"""

import logging
from typing import Dict

import pandas as pd
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)


class MLLogAnalyzer:
    """ML анализатор логов с использованием трансформеров.
    
    Логика написана коллегой и используется без изменений.
    """

    def __init__(self, similarity_threshold: float = 0.7):
        """Инициализация ML анализатора.

        Args:
            similarity_threshold: Порог уверенности для сопоставления аномалий
        """
        self.similarity_threshold = similarity_threshold
        self.model = None

    def _load_model(self):
        """Загружает модель трансформеров."""
        if self.model is None:
            logger.info("Загружаю модель sentence-transformers...")
            try:
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("Модель загружена успешно")
            except Exception as e:
                logger.error(f"Ошибка загрузки модели: {e}")
                raise

    def analyze_logs_with_ml(self, logs_df: pd.DataFrame, anomalies_problems_df: pd.DataFrame) -> pd.DataFrame:
        """Анализирует логи с использованием ML-модуля.

        Args:
            logs_df: DataFrame с логами (только WARNING и ERROR)
            anomalies_problems_df: DataFrame со словарем аномалий

        Returns:
            DataFrame с найденными проблемами и их локациями
        """
        logger.info(f"Начинаю ML анализ: {len(logs_df)} строк логов, {len(anomalies_problems_df)} аномалий")

        # Загружаем модель
        self._load_model()

        results = []

        # Получаем эмбеддинги известных аномалий
        known_anomalies = anomalies_problems_df["Аномалия"].astype(str).tolist()
        anomaly_embeddings = self.model.encode(known_anomalies, normalize_embeddings=True)
        
        logger.info(f"Начинаем анализ: {len(logs_df)} строк логов, {len(known_anomalies)} известных аномалий")
        warning_count = len(logs_df[logs_df["level"] == "WARNING"])
        error_count = len(logs_df[logs_df["level"] == "ERROR"])
        logger.info(f"В логах: {warning_count} WARNING, {error_count} ERROR")
        
        # Выводим примеры для отладки
        if warning_count > 0:
            sample_warning = logs_df[logs_df["level"] == "WARNING"].iloc[0]
            logger.info(f"Пример WARNING: text='{sample_warning['text']}'")
        if error_count > 0:
            sample_error = logs_df[logs_df["level"] == "ERROR"].iloc[0]
            logger.info(f"Пример ERROR: text='{sample_error['text']}'")
        if len(known_anomalies) > 0:
            logger.info(f"Пример аномалии из словаря: '{known_anomalies[0]}'")
            sample_problem = anomalies_problems_df.iloc[0]
            logger.info(f"Пример проблемы из словаря: '{sample_problem['Проблема']}'")

        # Список для новых аномалий (ниже порога)
        low_confidence_anomalies = []
        
        # Анализируем каждую WARNING строку
        for _, row in logs_df.iterrows():
            if row["level"] == "WARNING":
                text = str(row["text"]).strip()

                # Получаем эмбеддинг текущей строки
                text_embedding = self.model.encode(text, normalize_embeddings=True)

                # Вычисляем косинусное сходство со всеми известными аномалиями
                cosine_scores = util.cos_sim(text_embedding, anomaly_embeddings)[0]
                best_idx = cosine_scores.argmax().item()
                best_score = cosine_scores[best_idx].item()

                # Если сходство ниже порога — сохраняем для дальнейшего анализа
                if best_score < self.similarity_threshold:
                    logger.debug(f"Новая аномалия (score: {best_score:.3f}): {text[:50]}...")
                    
                    # Собираем информацию о полной строке лога
                    if 'full_line' in row and pd.notna(row['full_line']):
                        full_log_line = row['full_line']
                    else:
                        source = row.get('source', '')
                        if source and source != 'unknown':
                            full_log_line = f"{row['datetime']} {row['level']} {source}: {text}"
                        else:
                            full_log_line = f"{row['datetime']} {row['level']} {text}"
                    
                    low_confidence_anomalies.append({
                        'score': best_score,
                        'text': text,
                        'full_line': full_log_line,
                        'filename': row['filename'],
                        'line_number': row['line_number']
                    })
                    continue

                # Находим наиболее похожую аномалию и все её проблемы
                matched_anomaly = anomalies_problems_df.iloc[best_idx]
                matched_text = matched_anomaly["Аномалия"]
                
                logger.debug(f"WARNING сопоставлен с аномалией: {matched_text[:50]}... (score: {best_score:.3f})")

                # Получаем все проблемы для этой аномалии
                related_problems = anomalies_problems_df[
                    anomalies_problems_df["Аномалия"] == matched_text
                ]
                
                logger.debug(f"Найдено {len(related_problems)} связанных проблем")

                for _, ap in related_problems.iterrows():
                    anomaly_id = ap["ID аномалии"]
                    problem_id = ap["ID проблемы"]
                    problem_text = ap["Проблема"]
                    
                    logger.debug(f"Ищем ERROR с текстом: '{problem_text}'")

                    # Ищем ERROR строки с ТОЧНЫМ совпадением
                    problem_rows = logs_df[
                        (logs_df["level"] == "ERROR") &
                        (logs_df["text"].isin([problem_text]))  # ← Точное совпадение!
                    ]
                    
                    logger.debug(f"Найдено {len(problem_rows)} совпадающих ERROR строк")

                    for _, problem_row in problem_rows.iterrows():
                        # Формат: дата + уровень + источник + текст
                        # Используем full_line если есть, иначе собираем из частей
                        if 'full_line' in problem_row and pd.notna(problem_row['full_line']):
                            full_log_line = problem_row['full_line']
                        else:
                            # Собираем полную строку с источником 
                            source = problem_row.get('source', '')
                            if source and source != 'unknown':
                                full_log_line = f"{problem_row['datetime']} {problem_row['level']} {source}: {problem_row['text']}"
                            else:
                                # Если источника нет, формат без него
                                full_log_line = f"{problem_row['datetime']} {problem_row['level']} {problem_row['text']}"
                        
                        results.append({
                            'ID аномалии': anomaly_id,
                            'ID проблемы': problem_id,
                            'Файл с проблемой': problem_row['filename'],
                            '№ строки': problem_row['line_number'],
                            'Строка из лога': full_log_line
                        })

            # Добавляем ВСЕ новые аномалии с score > 0.5 (не только топ)
            top_new_anomalies = []
            if low_confidence_anomalies:
                # Сортируем по score (от большего к меньшему) и фильтруем score > 0.5
                low_confidence_anomalies.sort(key=lambda x: x['score'], reverse=True)
                top_new_anomalies = [a for a in low_confidence_anomalies if a['score'] > 0.5]
            
            logger.debug(f"Найдено {len(low_confidence_anomalies)} новых аномалий, добавляем {len(top_new_anomalies)}:")
            
            if top_new_anomalies:
                # Для каждой новой аномалии находим самую похожую СУЩЕСТВУЮЩУЮ аномалию
                for idx, anomaly in enumerate(top_new_anomalies, 1):
                    anomaly_text = anomaly['text']
                    anomaly_embedding = self.model.encode(anomaly_text, normalize_embeddings=True)
                    
                    # Вычисляем косинусное сходство со ВСЕМИ аномалиями из словаря
                    similarity_scores = util.cos_sim(anomaly_embedding, anomaly_embeddings)[0]
                    best_match_idx = similarity_scores.argmax().item()
                    best_match_score = similarity_scores[best_match_idx].item()
                    
                    # Берем ID аномалии и ID проблемы из самой похожей аномалии
                    matched_anomaly_row = anomalies_problems_df.iloc[best_match_idx]
                    matched_anomaly_id = matched_anomaly_row['ID аномалии']
                    matched_problem_id = matched_anomaly_row['ID проблемы']
                    matched_anomaly_text = matched_anomaly_row['Аномалия']
                    
                    logger.info(f"  Новая аномалия #{idx}: score={anomaly['score']:.3f} -> ID аномалии={matched_anomaly_id}, ID проблемы={matched_problem_id}")
                    logger.info(f"    Найденный текст: '{anomaly_text[:60]}...'")
                    logger.info(f"    Похожая аномалия (score={best_match_score:.3f}): '{matched_anomaly_text[:60]}...'")
                    
                    results.append({
                        'ID аномалии': matched_anomaly_id,  # ID самой похожей существующей аномалии
                        'ID проблемы': matched_problem_id,  # ID проблемы этой аномалии
                        'Файл с проблемой': anomaly['filename'],
                        '№ строки': anomaly['line_number'],
                        'Строка из лога': anomaly['full_line']
                    })

        result_df = pd.DataFrame(results)
        logger.info(f"ML анализ завершен: найдено {len(result_df)} проблем (включая новые аномалии)")

        return result_df

    def get_analysis_summary(self, results_df: pd.DataFrame) -> Dict:
        """Возвращает сводку анализа.

        Args:
            results_df: DataFrame с результатами анализа

        Returns:
            Словарь со статистикой анализа
        """
        if results_df.empty:
            return {
                'total_problems': 0,
                'unique_anomalies': 0,
                'unique_problems': 0,
                'unique_files': 0
            }

        # Статистика по проблемам
        total_problems = len(results_df)
        unique_anomalies = len(results_df['ID аномалии'].unique()) if 'ID аномалии' in results_df.columns else 0
        unique_problems = len(results_df['ID проблемы'].unique()) if 'ID проблемы' in results_df.columns else 0
        unique_files = len(results_df['Файл с проблемой'].unique()) if 'Файл с проблемой' in results_df.columns else 0

        return {
            'total_problems': total_problems,
            'unique_anomalies': unique_anomalies,
            'unique_problems': unique_problems,
            'unique_files': unique_files
        }

