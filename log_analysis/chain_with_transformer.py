import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sentence_transformers import SentenceTransformer, util
from log_to_df import collect_all_testcases
from typing import Dict, List, Any


def find_anomaly_problem_chain_transform(
        all_cases_df: pd.DataFrame,
        anomalies_problems: pd.DataFrame,
        similarity_threshold: float = 0.55
) -> pd.DataFrame:
    """
    Формирует связи между аномалиями (WARNING) и проблемами (ERROR)
    с применением семантического поиска и временной кластеризации.
    Использует кэширование эмбеддингов для ускорения работы.
    """

    model = SentenceTransformer("all-MiniLM-L6-v2")

    results: List[Dict[str, Any]] = []
    anomalies_problems = anomalies_problems.copy().reset_index(drop=True)
    anomalies_problems["Аномалия"] = anomalies_problems["Аномалия"].astype(str)
    anomalies_problems["Проблема"] = anomalies_problems["Проблема"].astype(str)

    max_anom_id: int = int(anomalies_problems["ID аномалии"].max()) if "ID аномалии" in anomalies_problems else 0
    max_prob_id: int = int(anomalies_problems["ID проблемы"].max()) if "ID проблемы" in anomalies_problems else 0

    # Кэш для эмбеддингов текстов
    emb_cache: Dict[str, np.ndarray] = {}

    def get_emb(text: str) -> np.ndarray:
        """Возвращает эмбеддинг текста с кэшированием."""
        text = str(text).strip() if not isinstance(text, str) else text.strip()
        if text not in emb_cache:
            emb_cache[text] = model.encode([text], normalize_embeddings=True)[0]
        return emb_cache[text]

    # Предварительно создаем кэш эмбеддингов известных аномалий
    known_anomalies = anomalies_problems["Аномалия"].fillna("").astype(str).tolist()
    known_anomalies = np.array(known_anomalies, dtype=str)
    anomaly_embeddings = model.encode(known_anomalies, normalize_embeddings=True)
    anomaly_emb_cache: Dict[str, np.ndarray] = dict(zip(known_anomalies, anomaly_embeddings))

    new_rows: List[Dict[str, Any]] = []

    # Обработка по сценариям
    for case_id, case_df in all_cases_df.groupby("id_scenario"):
        case_df["datetime"] = pd.to_datetime(case_df["datetime"])
        time_values = case_df["datetime"].astype("int64") // 10 ** 9
        avg_diff = np.mean(np.diff(np.sort(time_values))) if len(time_values) > 1 else 1

        # Кластеризация по времени
        dbscan = DBSCAN(eps=avg_diff * 10, min_samples=2)
        case_df["time_cluster"] = dbscan.fit_predict(time_values.values.reshape(-1, 1))

        # Обработка каждого временного кластера
        for cluster_id, cluster_df in case_df.groupby("time_cluster"):
            warnings_df = cluster_df[cluster_df["level"] == "WARNING"]
            errors_df = cluster_df[cluster_df["level"] == "ERROR"]

            if warnings_df.empty:
                continue

            # Эмбеддинги ошибок кластера (предварительно)
            error_texts = [str(t) for t in errors_df["text"].fillna("").tolist()]
            error_embs = np.stack([get_emb(t) for t in error_texts]) if len(error_texts) else np.zeros((0, 384))

            # Обработка каждой аномалии (WARNING)
            for _, warn_row in warnings_df.iterrows():
                warning_text = str(warn_row["text"]).strip()
                warning_emb = get_emb(warning_text)

                # Поиск наиболее похожей аномалии
                if anomaly_emb_cache:
                    scores = util.cos_sim(warning_emb, list(anomaly_emb_cache.values()))[0]
                    best_idx = scores.argmax().item()
                    best_score = float(scores[best_idx])
                    best_anom = list(anomaly_emb_cache.keys())[best_idx]
                else:
                    best_score, best_anom = 0.0, None

                # Существующая аномалия
                if best_score >= similarity_threshold:
                    matched = anomalies_problems[anomalies_problems["Аномалия"] == best_anom].iloc[0]
                    anom_id = matched["ID аномалии"]
                    related_probs = anomalies_problems[anomalies_problems["Аномалия"] == best_anom]

                    # Поиск соответствующей проблемы в текущем кластере
                    matched_prob = None
                    for _, p in related_probs.iterrows():
                        if errors_df["text"].str.contains(p["Проблема"], case=False, na=False, regex=False).any():
                            matched_prob = p
                            break

                    # Если проблема не найдена — ищем похожую ошибку
                    if matched_prob is None and len(error_embs) > 0:
                        sim_err_scores = util.cos_sim(warning_emb, error_embs)[0]
                        best_local_idx = sim_err_scores.argmax().item()
                        err_text = error_texts[best_local_idx]
                        max_prob_id += 1
                        matched_prob = {"ID проблемы": max_prob_id, "Проблема": err_text}
                        new_rows.append({
                            "ID аномалии": anom_id,
                            "Аномалия": best_anom,
                            "ID проблемы": max_prob_id,
                            "Проблема": err_text
                        })

                # Новая аномалия и проблема
                else:
                    max_anom_id += 1
                    new_anom_id = max_anom_id
                    if len(error_texts) > 0:
                        err_text = error_texts[0]
                        max_prob_id += 1
                        new_prob_id = max_prob_id
                        new_rows.append({
                            "ID аномалии": new_anom_id,
                            "Аномалия": warning_text,
                            "ID проблемы": new_prob_id,
                            "Проблема": err_text
                        })
                        anom_id = new_anom_id
                        matched_prob = {"ID проблемы": new_prob_id, "Проблема": err_text}
                        anomaly_emb_cache[warning_text] = warning_emb
                    else:
                        continue

                # Добавление результата
                results.append({
                    "id_scenario": case_id,
                    "ID аномалии": anom_id,
                    "Аномалия": warning_text,
                    "Уверенность": round(best_score, 3),
                    "ID проблемы": matched_prob["ID проблемы"],
                    "Файл с проблемой": warn_row.get("filename", ""),
                    "№ строки": int(warn_row.get("line_number", 0)),
                    "Строка из лога": warning_text
                })

    # Добавление новых пар в справочник
    if new_rows:
        anomalies_problems = pd.concat([anomalies_problems, pd.DataFrame(new_rows)], ignore_index=True)

    anomalies_problems.to_csv("anomalies_problems.csv", index=False, encoding="utf-8-sig", sep=";")
    return pd.DataFrame(results)


if __name__ == "__main__":
    anomalies_problems = pd.read_csv("anomalies_problems.csv", sep=";")
    all_tests = collect_all_testcases("../Test Cases")

    df = find_anomaly_problem_chain_transform(all_tests, anomalies_problems)
    df.to_csv("test_transform_2.csv", index=False, encoding="utf-8-sig")
