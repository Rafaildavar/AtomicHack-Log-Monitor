import pandas as pd
from sentence_transformers import SentenceTransformer, util
from log_to_df import logs_to_dataframe


def find_anomaly_problem_chain_transform(VC: pd.DataFrame,anomalies_problems: pd.DataFrame,similarity_threshold: float = 0.7):
    """
    Ищет наиболее похожую аномалию для WARNING через семантическое сходство
    и сопоставляет её с проблемой из словаря.
    """

    results = []

    # Модель эмбеддингов
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Эмбеддинги известных аномалий
    known_anomalies = anomalies_problems["Аномалия"].astype(str).tolist()
    anomaly_embeddings = model.encode(known_anomalies, normalize_embeddings=True)

    # Перебираем WARNING строки
    for _, row in VC.iterrows():
        if row["level"] == "WARNING":
            text = str(row["text"]).strip()

            # Эмбеддинг текущей строки
            emb = model.encode(text, normalize_embeddings=True)

            # Косинусное сходство со всеми известными аномалиями
            cosine_scores = util.cos_sim(emb, anomaly_embeddings)[0]
            best_idx = cosine_scores.argmax().item()
            best_score = cosine_scores[best_idx].item()

            # Если сходство меньше порога — пропускаем
            if best_score < similarity_threshold:
                results.append({
                    'ID аномалии': None,
                    'Аномалия': text,
                    'Уверенность': round(best_score, 3),
                    'ID проблемы': None,
                    'Файл с проблемой': None,
                    '№ строки': None,
                    'Строка из лога': None
                })
                continue

            # Находим наиболее похожую аномалию и все её проблемы
            matched_anomaly = anomalies_problems.iloc[best_idx]
            matched_text = matched_anomaly["Аномалия"]

            related_problems = anomalies_problems[
                anomalies_problems["Аномалия"] == matched_text
            ]

            for _, ap in related_problems.iterrows():
                anomaly_id = ap["ID аномалии"]
                problem_id = ap["ID проблемы"]
                problem_text = ap["Проблема"]

                # Ищем ERROR строки, где текст совпадает с проблемой
                problem_rows = VC[
                    (VC["level"] == "ERROR") &
                    (VC["text"].isin([problem_text]))
                ]

                for _, problem_row in problem_rows.iterrows():
                    results.append({
                        'ID аномалии': anomaly_id,
                        'Аномалия': text,
                        'Уверенность': round(best_score, 3),
                        'ID проблемы': problem_id,
                        'Файл с проблемой': problem_row['filename'],
                        '№ строки': problem_row['line_number'],
                        'Строка из лога': problem_row['text']
                    })

    return pd.DataFrame(results)


if __name__ == '__main__':
    anomalies_problems = pd.read_csv('../Validation_Cases/ValidationCase_1/anomalies_problems.csv', sep=';')
    VC3 = logs_to_dataframe('../Validation_Cases/ValidationCase_1')
    result_df = find_anomaly_problem_chain_transform(VC3, anomalies_problems)
    print(result_df.head())
