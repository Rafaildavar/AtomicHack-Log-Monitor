# 🚀 Быстрый старт AtomicHack Log Monitor 2.0

## Что сделано

✅ **Core-слой** - единая логика анализа (код коллеги без изменений)  
✅ **REST API** - FastAPI с автодокументацией  
✅ **Excel отчеты** - тот же формат, что для защиты хакатона

## Структура

```
├── core/              # Общая логика (используется ботом и API)
│   └── services/
│       ├── ml_analyzer.py      # ML-анализ коллеги
│       ├── log_parser.py       # Парсер логов коллеги
│       └── report_generator.py # Excel отчеты (формат защиты)
│
├── api/               # REST API
│   ├── main.py
│   └── requirements.txt
│
└── src/bot/           # Telegram бот (существующий)
```

## Запуск API

### 1. Установка зависимостей

```bash
# Создаем виртуальное окружение (если еще нет)
python -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate

# Устанавливаем зависимости для API
pip install -r api/requirements.txt
```

### 2. Запуск сервера

```bash
# Из корня проекта
cd api
python main.py
```

API запустится на http://localhost:8000

### 3. Открыть документацию

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Тестирование API

### Через Swagger UI (браузер)

1. Откройте http://localhost:8000/docs
2. Найдите endpoint `POST /api/v1/analyze`
3. Нажмите "Try it out"
4. Загрузите файл с логами
5. Нажмите "Execute"
6. Скачайте Excel отчет по ссылке из ответа

### Через cURL

```bash
# Анализ логов
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "log_file=@path/to/your/logs.txt" \
  -F "threshold=0.7"

# С пользовательским словарем
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "log_file=@logs.zip" \
  -F "anomalies_file=@anomalies_problems.csv"
```

### Через Python

```python
import requests

# Анализ файла
with open('logs.txt', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/analyze',
        files={'log_file': f},
        data={'threshold': 0.7}
    )

result = response.json()
print(f"Статус: {result['status']}")
print(f"Найдено проблем: {result['analysis']['ml_results']['total_problems']}")
print(f"Excel отчет: {result['excel_report']}")
```

## Запуск Telegram бота

Бот продолжает работать как раньше:

```bash
# Активировать venv
source .venv/bin/activate

# Запустить бота
cd src/bot
python -m main
```

## Важно

### Логика коллеги

Все функции анализа находятся в `core/services/`:
- **ml_analyzer.py** - точная копия логики из `src/bot/services/ml_log_analyzer.py`
- **log_parser.py** - адаптированная версия парсера (sync/async)
- **report_generator.py** - генерация Excel (формат для защиты)

### Формат Excel отчетов

Excel отчеты генерируются **в точности как для защиты**:
- Колонки: ID сценария, ID аномалии, ID проблемы, Файл с проблемой, № строки, Строка из лога
- Форматирование: голубые заголовки, центрирование текста
- Формат файла: .xlsx

### Единообразие

И бот, и API используют **одинаковые функции** из `core/`, поэтому:
- ✅ Результаты анализа идентичны
- ✅ Формат отчетов одинаковый
- ✅ Легко поддерживать код

## Что дальше?

### 1. Дополнительные интерфейсы (TODO #2)

Создать React приложение, которое:
- Использует API для анализа
- Красивый UI для загрузки файлов
- Интерактивные таблицы и графики
- История анализов

### 2. Доработка бота (TODO #3)

Улучшить функционал:
- История анализов пользователя
- Генерация API ключей через бота
- Настройка threshold через меню
- Уведомления о завершении анализа

### 3. Деплой (TODO #6)

- Docker контейнеры для всех сервисов
- CI/CD pipeline (GitHub Actions)
- Деплой на Railway/Render/Vercel

## Поддержка

При возникновении проблем:

1. Проверьте, что виртуальное окружение активировано
2. Убедитесь, что все зависимости установлены: `pip list`
3. Проверьте логи в консоли
4. Для API - откройте http://localhost:8000/health

## Команда

**Black Lotus** - 4-е место на AtomicHack Hackathon 2025  
Telegram Bot: @AtomicHackLogBot

