import pandas as pd
import plotly.express as px
from typing import Optional
import networkx as nx
from pyvis.network import Network


def visualize_logs(
    file_path: str,
    save_path: Optional[str] = None
) -> None:
    """
    Строит интерактивный график распределения логов по времени с цветовой дифференциацией уровней.

    Параметры:
        file_path (str): Путь к текстовому файлу с логами.
        save_path (Optional[str]): Путь для сохранения графика в формате HTML.
                                   Если None, график только отображается.

    Формат логов:
        <timestamp> <level> <message>
        Пример: 2025-11-25T16:45:00 INFO virtualization: Virtual network interface up
    """

    # Чтение и парсинг файла
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    data = []
    for line in lines:
        try:
            timestamp, level, message = line.strip().split(" ", 2)
            data.append({
                "time": timestamp,
                "level": level,
                "message": message
            })
        except ValueError:
            # Пропуск строк, не соответствующих формату
            continue

    # Формирование DataFrame
    df = pd.DataFrame(data)

    # Преобразование времени
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.dropna(subset=["time"])

    # Определение порядка уровней
    level_order = ["INFO", "WARNING", "ERROR"]
    df["level"] = pd.Categorical(df["level"], categories=level_order, ordered=True)

    # Цветовая схема
    color_map = {
        "INFO": "lightskyblue",
        "WARNING": "gold",
        "ERROR": "tomato"
    }

    # Построение графика
    fig = px.scatter(
        df,
        x="time",
        y="level",
        color="level",
        color_discrete_map=color_map,
        hover_data={"message": True, "time": False, "level": False},
        title=f"Распределение логов по времени в файле {file_path[file_path.rfind("/") + 1:]}"
    )

    # Настройки отображения
    fig.update_traces(marker=dict(size=10, opacity=0.8))
    fig.update_layout(
        xaxis_title="Время",
        yaxis_title="Уровень лога",
        yaxis_categoryorder="array",
        yaxis_categoryarray=level_order,
        legend_title="Тип лога",
        template="plotly_white",
        hoverlabel=dict(bgcolor="white", font_size=12)
    )

    # Отображение или сохранение графика
    if save_path:
        fig.write_html(save_path)

    else:
        fig.show()


def build_anomaly_problem_graph(
    chain_path: str,
    mapping_path: str,
    output_html: str = "anomaly_problem_graph.html"
) -> None:
    """
    Строит интерактивный граф связей между аномалиями и проблемами.

    :param chain_path: путь к CSV-файлу с сопоставлениями (ID сценария, ID аномалии, ID проблемы, ...).
    :param mapping_path: путь к CSV-файлу с описаниями аномалий и проблем.
    :param output_html: путь для сохранения HTML-файла с графом.
    """

    # === 1. Загрузка данных ===
    chain_df = pd.read_csv(chain_path, encoding="utf-8-sig")
    mapping_df = pd.read_csv(mapping_path, sep=";", encoding="utf-8-sig")

    # === 2. Подготовка словарей ===
    anomaly_texts = dict(zip(mapping_df["ID аномалии"], mapping_df["Аномалия"]))
    problem_texts = dict(zip(mapping_df["ID проблемы"], mapping_df["Проблема"]))

    # === 3. Создание графа ===
    G = nx.Graph()

    for _, row in chain_df.iterrows():
        anom_id = int(row["ID аномалии"])
        prob_id = int(row["ID проблемы"])

        anom_label = f"Аномалия {anom_id}: {anomaly_texts.get(anom_id, 'Неизвестно')}"
        prob_label = f"Проблема {prob_id}: {problem_texts.get(prob_id, 'Неизвестно')}"

        # Добавляем узлы с разным цветом
        G.add_node(anom_label, group="anomaly", color="#FFB347", shape="dot")
        G.add_node(prob_label, group="problem", color="#FF4C4C", shape="diamond")

        # Добавляем ребро между аномалией и проблемой
        G.add_edge(anom_label, prob_label)

    # === 4. Создание сети PyVis ===
    net = Network(
        height="800px",
        width="100%",
        bgcolor="#1e1e1e",
        font_color="white",
        directed=False,
    )

    # Перенос узлов и рёбер из NetworkX
    net.from_nx(G)

    # === 5. Настройки визуализации ===
    net.set_options("""
    {
      "nodes": {
        "font": {
          "size": 18
        },
        "scaling": {
          "min": 10,
          "max": 30
        }
      },
      "edges": {
        "color": {
          "inherit": true
        },
        "smooth": false
      },
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -2000,
          "centralGravity": 0.3,
          "springLength": 150,
          "springConstant": 0.04
        }
      }
    }
    """)

    # === 6. Сохранение ===
    try:
        net.show(output_html)
        print(f"Граф успешно сохранён в {output_html}")
    except Exception as e:
        print(f"Ошибка при вызове .show(): {e}")
        net.save_graph(output_html)
        print(f"Граф сохранён через save_graph() в {output_html}")





if __name__ == '__main__':
    # Пример вызова:
    visualize_logs("../../Test Cases/TestCase 7/app_server1_log.txt", "log_visualization.html")

    build_anomaly_problem_graph(
        chain_path="МИФИ_ИТОГ.csv",
        mapping_path="anomalies_problems.csv",
        output_html="graph.html"
    )
