# AtomicHack Log Monitor API - Dockerfile
# Команда Black Lotus

FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY api/ ./api/
COPY core/ ./core/
COPY src/bot/services/anomalies_problems.csv ./src/bot/services/

# Создаем директории для отчетов
RUN mkdir -p api/reports

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Открываем порт для API
EXPOSE 8001

# Запускаем FastAPI
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]

