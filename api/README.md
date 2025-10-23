# AtomicHack Log Monitor API

REST API для анализа логов с использованием ML. 

**Важно:** API использует те же функции анализа, что и Telegram бот (логика коллеги), и генерирует Excel отчеты в том же формате, что был для защиты на хакатоне.

## Особенности

- ✅ **Единая логика анализа** - используются те же функции из `core/`, что и в Telegram боте
- ✅ **Тот же формат Excel** - отчеты генерируются в точности как для защиты
- ✅ **ML-анализ коллеги** - без изменений алгоритма
- ✅ **Swagger документация** - автоматическая документация API
- ✅ **CORS поддержка** - для интеграции с внешними системами

## Установка

```bash
cd api
pip install -r requirements.txt
```

## Запуск

```bash
# Запуск API сервера
python main.py
```

API будет доступно по адресу: `http://localhost:8000`

## Документация

После запуска:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Анализ логов

**POST** `/api/v1/analyze`

Анализирует логи с использованием ML (логика коллеги).

**Параметры:**
- `log_file` (required): Файл с логами (.txt, .log, .zip)
- `anomalies_file` (optional): Словарь аномалий (если не указан, используется дефолтный)
- `threshold` (optional): Порог similarity (default: 0.7)

**Пример запроса:**

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "log_file=@logs.txt" \
  -F "threshold=0.7"
```

**Пример ответа:**

```json
{
  "status": "success",
  "analysis": {
    "basic_stats": {
      "total_lines": 1000,
      "error_count": 50,
      "warning_count": 150
    },
    "ml_results": {
      "total_problems": 45,
      "unique_anomalies": 12,
      "unique_problems": 15
    }
  },
  "results": [...],
  "excel_report": "/api/v1/download/analysis_report_logs.txt.xlsx"
}
```

### 2. Скачать отчет

**GET** `/api/v1/download/{filename}`

Скачивает сгенерированный Excel отчет (тот же формат, что для защиты).

### 3. Дефолтный словарь

**GET** `/api/v1/anomalies/default`

Получить дефолтный словарь аномалий.

### 4. Health Check

**GET** `/health`

Проверка состояния API.

## Интеграция в другие системы

### Python

```python
import requests

# Анализ логов
with open('logs.txt', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/analyze',
        files={'log_file': f},
        data={'threshold': 0.7}
    )

results = response.json()
print(f"Найдено проблем: {results['analysis']['ml_results']['total_problems']}")

# Скачать Excel отчет
if results['excel_report']:
    report_response = requests.get(f"http://localhost:8000{results['excel_report']}")
    with open('report.xlsx', 'wb') as f:
        f.write(report_response.content)
```

### JavaScript

```javascript
const formData = new FormData();
formData.append('log_file', fileInput.files[0]);
formData.append('threshold', '0.7');

fetch('http://localhost:8000/api/v1/analyze', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Результаты:', data);
    // Скачать отчет
    if (data.excel_report) {
        window.location.href = `http://localhost:8000${data.excel_report}`;
    }
});
```

### cURL

```bash
# Анализ с дефолтным словарем
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "log_file=@logs.txt" \
  -F "threshold=0.7"

# Анализ с пользовательским словарем
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "log_file=@logs.zip" \
  -F "anomalies_file=@anomalies_problems.csv" \
  -F "threshold=0.65"
```

## Архитектура

```
api/
├── main.py              # FastAPI приложение
├── requirements.txt     # Зависимости
└── README.md           # Документация

core/                    # Общая логика (используется ботом и API)
├── services/
│   ├── ml_analyzer.py      # ML-анализ (логика коллеги)
│   ├── log_parser.py       # Парсинг логов (логика коллеги)
│   └── report_generator.py # Excel отчеты (формат для защиты)
```

## Связь с Telegram ботом

API и бот используют **одинаковые функции** из `core/`:
- `MLLogAnalyzer` - ML-анализ
- `LogParser` - парсинг логов
- `ReportGenerator` - создание Excel отчетов

Это гарантирует:
- ✅ Одинаковые результаты анализа
- ✅ Один формат отчетов
- ✅ Единая логика обработки
- ✅ Легкость поддержки

## Производительность

- Первый запрос: ~10-15 сек (загрузка ML-модели)
- Последующие запросы: ~2-5 сек (зависит от размера логов)
- Поддержка ZIP архивов до 20MB

## Команда

**Black Lotus** - 4-е место на AtomicHack Hackathon 2025

## Лицензия

MIT

