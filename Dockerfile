# AtomicHack Log Monitor - Dockerfile
# Команда Black Lotus

FROM python:3.13-slim

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
COPY src/ ./src/
COPY .env.example .env

# Создаем директории для данных
RUN mkdir -p downloads reports

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV AIOHTTP_CLIENT_TIMEOUT=600

# Открываем порт (если потребуется webhook)
EXPOSE 8080

# Запускаем бота
CMD ["python", "-m", "src.bot.main"]

