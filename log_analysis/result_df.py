import pandas as pd
from log_to_df import logs_to_dataframe

def find_anomaly_problem_chain(VC, anomalies_problems):
    """Находит цепочку аномалия-проблема и создает результирующий DataFrame"""
    results = []

    for index, row in VC.iterrows():
        # Ищем аномалию по тексту из лога
        if row['level'] == 'WARNING':
            ap = anomalies_problems[anomalies_problems['Аномалия'] == row['text']]

            if not ap.empty:
                anomaly_id = ap['ID аномалии'].values[0]
                problem_text = ap['Проблема'].values

                # Ищем проблему в логах
                problem_rows = VC[VC['text'].isin(problem_text)]

                for _, problem_row in problem_rows.iterrows():
                    results.append({
                        'ID аномалии': anomaly_id,
                        'ID проблемы': ap['ID проблемы'].values[0],
                        'Файл с проблемой': problem_row['filename'],
                        '№ строки': problem_row['line_number'],
                        'Строка из лога': problem_row['text']
                    })

    return pd.DataFrame(results)


if __name__ == '__main__':
    anomalies_problems = pd.read_csv('../Validation_Cases/ValidationCase_1/anomalies_problems.csv', sep=';')
    VC3 = logs_to_dataframe('../Validation_Cases/ValidationCase_1')
    result_df = find_anomaly_problem_chain(VC3, anomalies_problems)
    print(result_df.head())