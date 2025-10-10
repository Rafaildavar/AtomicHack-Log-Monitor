import pandas as pd

def find_anomaly_problem_chain(VC2, anomalies_problems):
    """Находит цепочку аномалия-проблема и создает результирующий DataFrame"""
    results = []

    for index, row in VC2.iterrows():
        # Ищем аномалию по тексту из лога
        ap = anomalies_problems[anomalies_problems['Аномалия'] == row['text']]

        if not ap.empty:
            anomaly_id = ap['ID аномалии'].values[0]
            problem_text = ap['Проблема'].values[0]

            # Ищем проблему в логах
            problem_rows = VC2[VC2['text'] == problem_text]

            for _, problem_row in problem_rows.iterrows():
                results.append({
                    'ID аномалии': anomaly_id,
                    'ID проблемы': ap['ID проблемы'].values[0],
                    'Файл с проблемой': problem_row['filename'],
                    '№ строки': problem_row['line_number'],
                    'Строка из лога': problem_row['text']
                })

    return pd.DataFrame(results)