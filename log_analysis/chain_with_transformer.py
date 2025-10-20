import pandas as pd
from sentence_transformers import SentenceTransformer, util
from loguru import logger
from log_to_df import logs_to_dataframe, collect_all_testcases
import sys

logger.remove()

logger.add(
    "app.log",
    level="DEBUG",
    rotation="1 MB",  # ротация при достижении 1 МБ
    retention="10 days",  # хранить логи 10 дней
    compression="zip",  # сжимать старые логи
    enqueue=True,  # потокобезопасность
    mode="w"  # перезаписывать файл при каждом запуске
)



def find_anomaly_problem_chain_transform(all_cases_df: pd.DataFrame,
                                         anomalies_problems: pd.DataFrame,
                                         similarity_threshold: float = 0.55):
    """
    Находит связи между аномалиями (WARNING) и проблемами (ERROR) по семантическому сходству
    между текстами логов и справочником аномалий/проблем.
    """

    results = []
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Эмбеддинги известных аномалий из справочника
    known_anomalies = anomalies_problems["Аномалия"].astype(str).tolist()
    anomaly_embeddings = model.encode(known_anomalies, normalize_embeddings=True)

    # Группируем по кейсам
    for case_id, case_df in all_cases_df.groupby("id_scenario"):
        warnings_df = case_df[case_df["level"] == "WARNING"]
        errors_df = case_df[case_df["level"] == "ERROR"]

        if warnings_df.empty:
            continue

        for _, warn_row in warnings_df.iterrows():
            warning_text = str(warn_row["text"]).strip()
            warning_emb = model.encode(warning_text, normalize_embeddings=True)

            # Считаем косинусное сходство с базой аномалий
            scores = util.cos_sim(warning_emb, anomaly_embeddings)[0]
            best_idx = scores.argmax().item()
            best_score = scores[best_idx].item()

            if best_score < similarity_threshold:
                # Не нашли уверенного совпадения
                results.append({
                    'id_scenario': case_id,
                    'ID аномалии': None,
                    'Аномалия': warning_text,
                    'Уверенность': round(best_score, 3),
                    'ID проблемы': None,
                    'Файл с проблемой': None,
                    '№ строки': None,
                    'Строка из лога': None
                })
                logger.debug(f"None in anomaly: {warn_row}")
                continue


            # Находим аномалию и связанные проблемы
            matched_anomaly = anomalies_problems.iloc[best_idx]
            anomaly_text = matched_anomaly["Аномалия"]
            anomaly_id = matched_anomaly["ID аномалии"]

            related_problems = anomalies_problems[
                anomalies_problems["Аномалия"] == anomaly_text
            ][["ID проблемы", "Проблема"]].drop_duplicates()

            found_problem = False

            for _, prob in related_problems.iterrows():
                prob_text = prob["Проблема"]
                prob_id = prob["ID проблемы"]

                # Проверяем, есть ли такая ошибка в логах текущего кейса
                match = errors_df[errors_df["text"].str.contains(prob_text, case=False, na=False, regex=False)]

                if not match.empty:
                    found_problem = True
                    for _, err_row in match.iterrows():
                        results.append({
                            'id_scenario': case_id,
                            'ID аномалии': anomaly_id,
                            'Аномалия': warning_text,
                            'Уверенность': round(best_score, 3),
                            'ID проблемы': prob_id,
                            'Файл с проблемой': err_row["filename"],
                            '№ строки': err_row["line_number"],
                            'Строка из лога': f"{err_row['datetime']} {err_row['level']} {err_row['source']}: {err_row['text']}"
                        })
                else:
                    logger.debug(f"{prob_text} not in match")
                    logger.debug(f"errors_df: {errors_df['text']}")

            # Если проблема не найдена в логах — тоже сохраняем
            if not found_problem:
                results.append({
                    'id_scenario': case_id,
                    'ID аномалии': anomaly_id,
                    'Аномалия': warning_text,
                    'Уверенность': round(best_score, 3),
                    'ID проблемы': None,
                    'Файл с проблемой': None,
                    '№ строки': None,
                    'Строка из лога': None
                })
                logger.debug(f"None in problem: {warn_row}")


    return pd.DataFrame(results)

if __name__ == '__main__':
    anomalies_problems = pd.read_csv('../Validation_Cases/ValidationCase_1/anomalies_problems.csv', sep=';')
    all_tests = collect_all_testcases('../Test Cases')
    df = find_anomaly_problem_chain_transform(all_tests, anomalies_problems)