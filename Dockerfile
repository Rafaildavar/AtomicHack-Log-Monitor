# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем системные зависимости для компиляции пакетов
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY api/requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Открываем порт
EXPOSE 8001

# Команда запуска (Render автоматически установит PORT)
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8001}

