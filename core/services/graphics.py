import pandas as pd
import plotly.express as px
from typing import Optional


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


if __name__ == '__main__':
    # Пример вызова:
    visualize_logs("../../Test Cases/TestCase 7/app_server1_log.txt", "log_visualization.html")
