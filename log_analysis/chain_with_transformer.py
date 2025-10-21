import pandas as pd
from sentence_transformers import SentenceTransformer, util
from loguru import logger
from log_to_df import logs_to_dataframe, collect_all_testcases
import sys
from sklearn.cluster import DBSCAN
import numpy as np

logger.remove()

logger.add(
    "app.log",
    level="INFO",
    rotation="1 MB",  # ротация при достижении 1 МБ
    retention="10 days",  # хранить логи 10 дней
    compression="zip",  # сжимать старые логи
    enqueue=True,  # потокобезопасность
    mode="w"  # перезаписывать файл при каждом запуске
)

def time_cluster(df: pd.DataFrame):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['timestamp_sec'] = df['datetime'].astype('int64') // 10 ** 9

    # Автоматическое определение eps на основе среднего расстояния
    time_values = df['timestamp_sec'].values.reshape(-1, 1)
    time_sorted = np.sort(time_values, axis=0)
    time_diffs = np.diff(time_sorted, axis=0)
    avg_diff = np.mean(time_diffs)

    dbscan = DBSCAN(
        eps=avg_diff * 10,  # в 10 раз больше среднего интервала
        min_samples=2,
        metric='euclidean'
    )
    time_clusters = dbscan.fit_predict(time_values)
    df['time_cluster'] = time_clusters

    cluster_dfs = {}
    for cluster_id in np.unique(time_clusters):
        cluster_mask = df['time_cluster'] == cluster_id
        cluster_dfs[cluster_id] = df[cluster_mask].drop(['time_cluster', 'timestamp_sec'], axis=1)

    return cluster_dfs

def find_anomaly_problem_chain_transform(all_cases_df: pd.DataFrame,
                                         anomalies_problems: pd.DataFrame,
                                         similarity_threshold: float = 0.55):
    """
    Находит связи между аномалиями (WARNING) и проблемами (ERROR)
    по семантическому сходству, с учётом временной кластеризации.

    Поведение при отсутствии точного соответствия:
    - пытаемся найти похожую ERROR в кластере семантически;
    - если нет похожих — берём любую ERROR из кластера (nearest by time) и
      создаём новую пару (добавляем запись в anomalies_problems).
    - если похожей аномалии нет (best_score < threshold) — создаём новую аномалию
      и связываем её с выбранной проблемой (также создаём новую проблему, если требуется).
    """
    results = []
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Сделаем копию словаря, чтобы можно было добавлять новые строки
    anomalies_problems = anomalies_problems.copy().reset_index(drop=True)
    # Приведём к строкам
    anomalies_problems["Аномалия"] = anomalies_problems["Аномалия"].astype(str)
    anomalies_problems["Проблема"] = anomalies_problems["Проблема"].astype(str)

    # текущие max id для генерации новых
    try:
        max_anom_id = int(anomalies_problems["ID аномалии"].max())
    except:
        max_anom_id = 0
    try:
        max_prob_id = int(anomalies_problems["ID проблемы"].max())
    except:
        max_prob_id = 0

    # Эмбеддинги известных аномалий
    known_anomalies = anomalies_problems["Аномалия"].astype(str).tolist()
    anomaly_embeddings = model.encode(known_anomalies, normalize_embeddings=True) if known_anomalies else []

    # Функция для выбора ближайшей ошибки по времени внутри кластера
    def choose_nearest_error(warn_time, errors_df):
        if errors_df.empty:
            return None
        # безопасно привести datetime
        try:
            warn_dt = pd.to_datetime(warn_time)
            errs = errors_df.copy()
            errs["__dt"] = pd.to_datetime(errs["datetime"], errors="coerce")
            errs["__diff"] = (errs["__dt"] - warn_dt).abs()
            errs = errs.sort_values("__diff")
            return errs.iloc[0]
        except Exception:
            # если с датами проблемы — просто вернуть первую строку
            return errors_df.iloc[0]

    # Проходим по кейсам
    for case_id, case_df in all_cases_df.groupby("id_scenario"):
        clusters = time_cluster(case_df)

        for cluster_id, cluster_df in clusters.items():
            warnings_df = cluster_df[cluster_df["level"] == "WARNING"].reset_index(drop=True)
            errors_df = cluster_df[cluster_df["level"] == "ERROR"].reset_index(drop=True)

            if warnings_df.empty:
                continue

            # Предвычислим эмбеддинги ошибок в кластере для семантического поиска
            local_err_texts = errors_df["text"].astype(str).tolist() if not errors_df.empty else []
            local_err_embs = model.encode(local_err_texts, normalize_embeddings=True) if local_err_texts else []

            for _, warn_row in warnings_df.iterrows():
                warning_text = str(warn_row["text"]).strip()
                warning_emb = model.encode(warning_text, normalize_embeddings=True)

                assigned_anomaly_id = None
                assigned_problem_id = None
                assigned_problem_text = None
                assigned_file = "<unknown>"
                assigned_line = 0
                assigned_log_row = None
                confidence = 0.0

                # 1) Пробуем найти похожую известную аномалию
                if len(anomaly_embeddings) > 0:
                    scores = util.cos_sim(warning_emb, anomaly_embeddings)[0]
                    best_idx = int(scores.argmax().item())
                    best_score = float(scores[best_idx].item())
                else:
                    best_idx = None
                    best_score = 0.0

                # Если похожая аномалия найдена
                if best_score >= similarity_threshold and best_idx is not None:
                    matched_anomaly = anomalies_problems.iloc[best_idx]
                    anomaly_text = matched_anomaly["Аномалия"]
                    anomaly_id = int(matched_anomaly["ID аномалии"])
                    confidence = best_score
                    assigned_anomaly_id = anomaly_id

                    # Перебираем связанные проблемы из словаря — сначала точное str.contains в кластере
                    related_problems = anomalies_problems[anomalies_problems["Аномалия"] == anomaly_text][["ID проблемы", "Проблема"]].drop_duplicates()

                    found_problem = False
                    for _, prob in related_problems.iterrows():
                        prob_text = str(prob["Проблема"])
                        prob_id = int(prob["ID проблемы"])
                        match = errors_df[errors_df["text"].astype(str).str.contains(prob_text, case=False, na=False, regex=False)]
                        if not match.empty:
                            found_problem = True
                            err_row = match.iloc[0]
                            assigned_problem_id = prob_id
                            assigned_problem_text = prob_text
                            assigned_file = err_row.get("filename", "<unknown>")
                            assigned_line = int(err_row.get("line_number", 0)) if not pd.isna(err_row.get("line_number", None)) else 0
                            assigned_log_row = f"{err_row['datetime']} {err_row['level']} {err_row['source']}: {err_row['text']}"
                            break

                    # Если не нашли точного совпадения, ищем похожую ERROR семантически в кластере
                    if not found_problem and len(local_err_embs) > 0:
                        sim_err_scores = util.cos_sim(warning_emb, local_err_embs)[0].cpu().numpy()
                        best_local_idx = int(sim_err_scores.argmax())
                        best_local_score = float(sim_err_scores[best_local_idx])
                        if best_local_score >= 0.45:  # жёсткость порога для ошибки (можно вынести как параметр)
                            err_row = errors_df.iloc[best_local_idx]
                            # проверим, есть ли такая проблема в словаре
                            matched_prob = anomalies_problems[anomalies_problems["Проблема"].str.lower() == str(err_row["text"]).lower()]
                            if not matched_prob.empty:
                                assigned_problem_id = int(matched_prob.iloc[0]["ID проблемы"])
                                assigned_problem_text = matched_prob.iloc[0]["Проблема"]
                            else:
                                # создаём новую проблему в словаре и привязываем
                                max_prob_id += 1
                                assigned_problem_id = int(max_prob_id)
                                assigned_problem_text = str(err_row["text"])
                                anomalies_problems = pd.concat([anomalies_problems, pd.DataFrame([{
                                    "ID аномалии": anomaly_id,
                                    "Аномалия": anomaly_text,
                                    "ID проблемы": assigned_problem_id,
                                    "Проблема": assigned_problem_text
                                }])], ignore_index=True)
                                # обнов_embeddings не необходим для аномалий (мы добавили проблему)
                            assigned_file = err_row.get("filename", "<unknown>")
                            assigned_line = int(err_row.get("line_number", 0)) if not pd.isna(err_row.get("line_number", None)) else 0
                            assigned_log_row = f"{err_row['datetime']} {err_row['level']} {err_row['source']}: {err_row['text']}"
                            found_problem = True

                    # Если всё ещё не нашли — берём nearest error из кластера и создаём новую проблему (и добавляем запись)
                    if not found_problem:
                        if not errors_df.empty:
                            nearest_err = choose_nearest_error(warn_row["datetime"], errors_df)
                            err_row = nearest_err
                            max_prob_id += 1
                            assigned_problem_id = int(max_prob_id)
                            assigned_problem_text = str(err_row["text"])
                            assigned_file = err_row.get("filename", "<unknown>")
                            assigned_line = int(err_row.get("line_number", 0)) if not pd.isna(err_row.get("line_number", None)) else 0
                            assigned_log_row = f"{err_row['datetime']} {err_row['level']} {err_row['source']}: {err_row['text']}"
                            # Добавляем новую пару в словарь: существующая аномалия -> новая проблема
                            anomalies_problems = pd.concat([anomalies_problems, pd.DataFrame([{
                                "ID аномалии": anomaly_id,
                                "Аномалия": anomaly_text,
                                "ID проблемы": assigned_problem_id,
                                "Проблема": assigned_problem_text
                            }])], ignore_index=True)
                        else:
                            # нет ошибок в кластере — создаём заглушку проблемы
                            max_prob_id += 1
                            assigned_problem_id = int(max_prob_id)
                            assigned_problem_text = "UNKNOWN_PROBLEM"
                            assigned_file = "<unknown>"
                            assigned_line = 0
                            assigned_log_row = assigned_problem_text
                            anomalies_problems = pd.concat([anomalies_problems, pd.DataFrame([{
                                "ID аномалии": anomaly_id,
                                "Аномалия": anomaly_text,
                                "ID проблемы": assigned_problem_id,
                                "Проблема": assigned_problem_text
                            }])], ignore_index=True)

                else:
                    # 2) НЕ нашли похожую аномалию в словаре (best_score < similarity_threshold)
                    # В этом случае: пытаемся найти похожую ERROR в кластере семантически;
                    # если найдена — создаём НОВУЮ аномалию и привязываем к найденной проблеме;
                    # если нет — берём любую ERROR из кластера и создаём новую аномалию + новую проблему.

                    if not errors_df.empty and len(local_err_embs) > 0:
                        sim_err_scores = util.cos_sim(warning_emb, local_err_embs)[0].cpu().numpy()
                        best_local_idx = int(sim_err_scores.argmax())
                        best_local_score = float(sim_err_scores[best_local_idx])

                        if best_local_score >= 0.45:
                            # связываем с найденной локальной ошибкой и создаём новую аномалию
                            err_row = errors_df.iloc[best_local_idx]
                            # создаём новую аномалию
                            max_anom_id += 1
                            new_anom_id = int(max_anom_id)
                            anomalies_problems = pd.concat([anomalies_problems, pd.DataFrame([{
                                "ID аномалии": new_anom_id,
                                "Аномалия": warning_text,
                                "ID проблемы": None,
                                "Проблема": ""
                            }])], ignore_index=True)
                            # проверим есть ли проблема в словаре
                            matched_prob = anomalies_problems[anomalies_problems["Проблема"].str.lower() == str(err_row["text"]).lower()]
                            if not matched_prob.empty:
                                assigned_problem_id = int(matched_prob.iloc[0]["ID проблемы"])
                                assigned_problem_text = matched_prob.iloc[0]["Проблема"]
                            else:
                                max_prob_id += 1
                                assigned_problem_id = int(max_prob_id)
                                assigned_problem_text = str(err_row["text"])
                                # добавляем связь
                                anomalies_problems = pd.concat([anomalies_problems, pd.DataFrame([{
                                    "ID аномалии": new_anom_id,
                                    "Аномалия": warning_text,
                                    "ID проблемы": assigned_problem_id,
                                    "Проблема": assigned_problem_text
                                }])], ignore_index=True)

                            assigned_anomaly_id = new_anom_id
                            assigned_file = err_row.get("filename", "<unknown>")
                            assigned_line = int(err_row.get("line_number", 0)) if not pd.isna(err_row.get("line_number", None)) else 0
                            assigned_log_row = f"{err_row['datetime']} {err_row['level']} {err_row['source']}: {err_row['text']}"
                            confidence = best_local_score
                        else:
                            # нет похожих ошибок семантически — берём nearest error и создаём новую аномалию + проблему
                            nearest_err = choose_nearest_error(warn_row["datetime"], errors_df)
                            err_row = nearest_err
                            max_anom_id += 1
                            new_anom_id = int(max_anom_id)
                            max_prob_id += 1
                            new_prob_id = int(max_prob_id)
                            anomalies_problems = pd.concat([anomalies_problems, pd.DataFrame([{
                                "ID аномалии": new_anom_id,
                                "Аномалия": warning_text,
                                "ID проблемы": new_prob_id,
                                "Проблема": str(err_row["text"])
                            }])], ignore_index=True)

                            assigned_anomaly_id = new_anom_id
                            assigned_problem_id = new_prob_id
                            assigned_problem_text = str(err_row["text"])
                            assigned_file = err_row.get("filename", "<unknown>")
                            assigned_line = int(err_row.get("line_number", 0)) if not pd.isna(err_row.get("line_number", None)) else 0
                            assigned_log_row = f"{err_row['datetime']} {err_row['level']} {err_row['source']}: {err_row['text']}"
                            confidence = 0.0
                    else:
                        # нет ошибок в кластере — создаём новую аномалию и новую проблему-заглушку
                        max_anom_id += 1
                        new_anom_id = int(max_anom_id)
                        max_prob_id += 1
                        new_prob_id = int(max_prob_id)
                        anomalies_problems = pd.concat([anomalies_problems, pd.DataFrame([{
                            "ID аномалии": new_anom_id,
                            "Аномалия": warning_text,
                            "ID проблемы": new_prob_id,
                            "Проблема": "UNKNOWN_PROBLEM"
                        }])], ignore_index=True)

                        assigned_anomaly_id = new_anom_id
                        assigned_problem_id = new_prob_id
                        assigned_problem_text = "UNKNOWN_PROBLEM"
                        assigned_file = "<unknown>"
                        assigned_line = 0
                        assigned_log_row = assigned_problem_text
                        confidence = 0.0

                # Вставляем запись в results — без NaN
                results.append({
                    'id_scenario': case_id,
                    'ID аномалии': int(assigned_anomaly_id) if assigned_anomaly_id is not None else 0,
                    'Аномалия': warning_text,
                    'Уверенность': round(float(confidence), 3),
                    'ID проблемы': int(assigned_problem_id) if assigned_problem_id is not None else 0,
                    'Файл с проблемой': assigned_file,
                    '№ строки': int(assigned_line),
                    'Строка из лога': assigned_log_row if assigned_log_row is not None else ""
                })

                # Обновляем anomaly_embeddings (добавленные аномалии) — чтобы последующие WARN могли их найти
                known_anomalies = anomalies_problems["Аномалия"].astype(str).tolist()
                anomaly_embeddings = model.encode(known_anomalies, normalize_embeddings=True) if known_anomalies else []

    # при желании можно сохранить обновлённый словарь вне этой функции (не делаю автоматически здесь)
    return pd.DataFrame(results)



if __name__ == '__main__':
    anomalies_problems = pd.read_csv('../Validation_Cases/ValidationCase_1/anomalies_problems.csv', sep=';')
    all_tests = collect_all_testcases('../Test Cases')
    df = find_anomaly_problem_chain_transform(all_tests, anomalies_problems)
    df.to_csv("test_trnsform.csv", index=False, encoding="utf-8-sig")