"""Интегратор ML-модуля анализа логов для Telegram бота."""

import logging
import os
from typing import Dict, List, Tuple

import pandas as pd
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)


class MLLogAnalyzer:
    """ML анализатор логов с использованием трансформеров."""

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

                # Если сходство ниже порога — пропускаем (не добавляем в результат)
                if best_score < self.similarity_threshold:
                    logger.debug(f"Аномалия с низкой уверенностью пропущена: {text[:50]}... (score: {best_score})")
                    continue

                # Находим наиболее похожую аномалию и все её проблемы
                matched_anomaly = anomalies_problems_df.iloc[best_idx]
                matched_text = matched_anomaly["Аномалия"]

                # Получаем все проблемы для этой аномалии
                related_problems = anomalies_problems_df[
                    anomalies_problems_df["Аномалия"] == matched_text
                ]

                for _, ap in related_problems.iterrows():
                    anomaly_id = ap["ID аномалии"]
                    problem_id = ap["ID проблемы"]
                    problem_text = ap["Проблема"]

                    # Ищем ERROR строки, где текст совпадает с проблемой
                    problem_rows = logs_df[
                        (logs_df["level"] == "ERROR") &
                        (logs_df["text"].str.contains(str(problem_text), na=False))
                    ]

                    for _, problem_row in problem_rows.iterrows():
                        # Формат точно соответствует ValidationCases.xlsx
                        results.append({
                            'ID аномалии': anomaly_id,
                            'ID проблемы': problem_id,
                            'Файл с проблемой': problem_row['filename'],
                            '№ строки': problem_row['line_number'],
                            'Строка из лога': problem_row['text']
                        })

        result_df = pd.DataFrame(results)
        logger.info(f"ML анализ завершен: найдено {len(result_df)} проблем")

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
