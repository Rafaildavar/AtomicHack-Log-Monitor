# 🌐 REST API для анализа логов - Руководство

## 📌 Что это

REST API, который использует **твою логику анализа логов** из бота и делает её доступной через HTTP.

**Важно:** API использует **твой код без изменений** - всё, что ты написал для бота, теперь работает и через API.

---

## 🎯 Зачем это нужно

Теперь анализ логов можно использовать:
- ✅ В Telegram боте (как раньше)
- ✅ Через HTTP запросы (для интеграции в другие системы)
- ✅ Из любого языка программирования (Python, JS, Go, etc.)

**Твоя логика в одном месте → работает везде.**

---

## 📁 Структура (что где лежит)

```
core/services/              # Твоя логика (вынесена сюда)
├── ml_analyzer.py         # Твой ML-анализ (БЕЗ ИЗМЕНЕНИЙ)
├── log_parser.py          # Твой парсер логов
└── report_generator.py    # Генерация Excel (как для защиты)

api/                       # REST API (использует твою логику)
├── main.py               # FastAPI приложение
└── requirements.txt      # Зависимости
```

---

## 🚀 Как запустить

### 1. Установить зависимости

```bash
# Из корня проекта
pip install -r api/requirements.txt
```

Что устанавливается:
- `fastapi` - веб-фреймворк
- `uvicorn` - сервер
- `sentence-transformers`, `pandas`, `torch` - твои ML библиотеки
- `openpyxl` - для Excel

### 2. Запустить сервер

```bash
cd api
python main.py
```

Или из корня проекта:

```bash
python api/main.py
```

### 3. Проверить что работает

Открой в браузере: **http://localhost:8000**

Должно показать:
```json
{
  "message": "AtomicHack Log Monitor API",
  "version": "1.0.0",
  "team": "Black Lotus",
  "status": "running"
}
```

---

## 📖 API Endpoints (что можно делать)

### 1. **POST /api/v1/analyze** - Главный endpoint (анализ логов)

**Что делает:** Анализирует логи используя **твой ML-код**

**Параметры:**
- `log_file` (обязательно) - файл с логами (.txt, .log, .zip)
- `anomalies_file` (опционально) - словарь аномалий
- `threshold` (опционально) - порог ML (default: 0.7)

**Пример через cURL:**

```bash
# С дефолтным словарем
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "log_file=@logs.txt" \
  -F "threshold=0.7"

# С пользовательским словарем
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "log_file=@logs.txt" \
  -F "anomalies_file=@anomalies_problems.csv" \
  -F "threshold=0.65"
```

**Ответ:**

```json
{
  "status": "success",
  "analysis": {
    "basic_stats": {
      "total_lines": 1000,
      "error_count": 50,
      "warning_count": 150,
      "info_count": 800
    },
    "ml_results": {
      "total_problems": 45,
      "unique_anomalies": 12,
      "unique_problems": 15,
      "unique_files": 3
    },
    "threshold_used": 0.7
  },
  "results": [
    {
      "ID аномалии": 5,
      "ID проблемы": 12,
      "Файл с проблемой": "logs.txt",
      "№ строки": 234,
      "Строка из лога": "2025-10-02T13:18:00 ERROR hardware: Fan failure detected"
    }
  ],
  "excel_report": "/api/v1/download/analysis_report_logs.txt.xlsx"
}
```

### 2. **GET /api/v1/download/{filename}** - Скачать Excel отчет

**Что делает:** Возвращает Excel файл (формат как для защиты)

**Пример:**

```bash
curl -O "http://localhost:8000/api/v1/download/analysis_report_logs.txt.xlsx"
```

### 3. **GET /api/v1/anomalies/default** - Дефолтный словарь

**Что делает:** Возвращает твой дефолтный словарь аномалий

**Пример:**

```bash
curl -O "http://localhost:8000/api/v1/anomalies/default"
```

### 4. **GET /health** - Проверка здоровья API

**Что делает:** Показывает статус API и ML-модели

**Пример:**

```bash
curl "http://localhost:8000/health"
```

**Ответ:**

```json
{
  "status": "healthy",
  "ml_model": "loaded",
  "services": {
    "ml_analyzer": "ready",
    "log_parser": "ready",
    "report_generator": "ready"
  }
}
```

### 5. **GET /docs** - Swagger документация

Автоматическая интерактивная документация.

Открой в браузере: **http://localhost:8000/docs**

Там можно:
- Увидеть все endpoints
- Протестировать прямо в браузере
- Посмотреть примеры запросов/ответов

---

## 💻 Как использовать из кода

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

result = response.json()
print(f"Статус: {result['status']}")
print(f"Найдено проблем: {result['analysis']['ml_results']['total_problems']}")

# Скачать Excel отчет
if result['excel_report']:
    excel_url = f"http://localhost:8000{result['excel_report']}"
    excel_response = requests.get(excel_url)
    
    with open('report.xlsx', 'wb') as f:
        f.write(excel_response.content)
    
    print("Excel отчет сохранен: report.xlsx")
```

### JavaScript (Node.js)

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

// Анализ логов
const form = new FormData();
form.append('log_file', fs.createReadStream('logs.txt'));
form.append('threshold', '0.7');

axios.post('http://localhost:8000/api/v1/analyze', form, {
    headers: form.getHeaders()
})
.then(response => {
    console.log('Статус:', response.data.status);
    console.log('Проблем найдено:', response.data.analysis.ml_results.total_problems);
    
    // Скачать Excel
    if (response.data.excel_report) {
        const excelUrl = `http://localhost:8000${response.data.excel_report}`;
        return axios.get(excelUrl, { responseType: 'stream' });
    }
})
.then(excelResponse => {
    excelResponse.data.pipe(fs.createWriteStream('report.xlsx'));
    console.log('Excel отчет сохранен');
});
```

### JavaScript (браузер)

```javascript
// HTML форма
<input type="file" id="logFile">
<button onclick="analyzeLog()">Анализировать</button>

// JavaScript
async function analyzeLog() {
    const fileInput = document.getElementById('logFile');
    const formData = new FormData();
    formData.append('log_file', fileInput.files[0]);
    formData.append('threshold', '0.7');
    
    const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    console.log('Найдено проблем:', result.analysis.ml_results.total_problems);
    
    // Скачать Excel
    if (result.excel_report) {
        window.location.href = `http://localhost:8000${result.excel_report}`;
    }
}
```

---

## 🔧 Как это работает внутри

### Что происходит когда отправляешь запрос:

```
1. Прием файла
   ↓
2. Извлечение (если ZIP)
   ↓ LogParser.extract_zip()
3. Парсинг логов
   ↓ LogParser.parse_log_files()      ← ТВОЯ ЛОГИКА
4. Загрузка словаря аномалий
   ↓
5. ML-анализ
   ↓ MLLogAnalyzer.analyze_logs_with_ml()  ← ТВОЯ ЛОГИКА
6. Генерация Excel
   ↓ ReportGenerator.create_excel_report()  ← ТВОЯ ЛОГИКА (формат защиты)
7. Возврат результата (JSON + Excel)
```

### Код из api/main.py (упрощенно):

```python
from core.services.ml_analyzer import MLLogAnalyzer      # Твой код
from core.services.log_parser import LogParser          # Твой код
from core.services.report_generator import ReportGenerator  # Твой код

@app.post("/api/v1/analyze")
async def analyze_logs(log_file: UploadFile, threshold: float = 0.7):
    # 1. Парсим логи (ТВОЯ ЛОГИКА)
    log_parser = LogParser()
    logs_df = log_parser.parse_log_files([log_file_path])
    
    # 2. ML-анализ (ТВОЯ ЛОГИКА)
    ml_analyzer = MLLogAnalyzer(similarity_threshold=threshold)
    results_df = ml_analyzer.analyze_logs_with_ml(logs_df, anomalies_df)
    
    # 3. Генерируем Excel (ТВОЯ ЛОГИКА - формат защиты)
    report_generator = ReportGenerator()
    excel_path = report_generator.create_excel_report(results)
    
    # 4. Возвращаем результат
    return {
        "status": "success",
        "analysis": {...},
        "results": results_df.to_dict('records'),
        "excel_report": f"/api/v1/download/{filename}"
    }
```

**Важно:** Это **твой код** из `core/services/`, API просто предоставляет к нему HTTP интерфейс.

---

## 🎯 Примеры использования

### 1. Быстрый тест через Swagger UI

1. Запусти API: `python api/main.py`
2. Открой: http://localhost:8000/docs
3. Найди `POST /api/v1/analyze`
4. Нажми "Try it out"
5. Загрузи файл логов
6. Нажми "Execute"
7. Получи результат + скачай Excel

### 2. Интеграция в систему мониторинга

```python
# Скрипт, который запускается каждый час
import requests
from datetime import datetime

def check_logs():
    # Собираем логи за последний час
    logs = collect_last_hour_logs()
    
    # Отправляем на анализ
    response = requests.post(
        'http://localhost:8000/api/v1/analyze',
        files={'log_file': logs}
    )
    
    result = response.json()
    
    # Если найдены проблемы - шлём алерт
    if result['analysis']['ml_results']['total_problems'] > 0:
        send_alert(
            f"Обнаружено {result['analysis']['ml_results']['total_problems']} проблем!",
            excel_report=result['excel_report']
        )
```

### 3. Batch обработка

```python
import os
import requests

# Анализируем все логи в папке
log_files = [f for f in os.listdir('logs/') if f.endswith('.txt')]

for log_file in log_files:
    with open(f'logs/{log_file}', 'rb') as f:
        response = requests.post(
            'http://localhost:8000/api/v1/analyze',
            files={'log_file': f}
        )
        
        result = response.json()
        print(f"{log_file}: {result['analysis']['ml_results']['total_problems']} проблем")
```

---

## 📊 Что возвращает API

### Структура ответа:

```json
{
  "status": "success",              // Статус выполнения
  
  "analysis": {
    "basic_stats": {                // Базовая статистика
      "total_lines": 1000,         // Всего строк в логах
      "error_count": 50,           // Количество ERROR
      "warning_count": 150,        // Количество WARNING
      "info_count": 800            // Количество INFO
    },
    
    "ml_results": {                 // Результаты ML-анализа (ТВОЙ АЛГОРИТМ)
      "total_problems": 45,        // Всего найдено проблем
      "unique_anomalies": 12,      // Уникальных аномалий
      "unique_problems": 15,       // Уникальных проблем
      "unique_files": 3            // Файлов с проблемами
    },
    
    "threshold_used": 0.7          // Использованный порог
  },
  
  "results": [                      // Детальные результаты
    {
      "ID аномалии": 5,
      "ID проблемы": 12,
      "Файл с проблемой": "logs.txt",
      "№ строки": 234,
      "Строка из лога": "2025-10-02T13:18:00 ERROR hardware: Fan failure"
    }
  ],
  
  "excel_report": "/api/v1/download/report.xlsx"  // Ссылка на Excel
}
```

---

## ⚙️ Настройки

### Порог similarity (threshold)

Твой ML-алгоритм использует порог для определения похожести аномалий:

- **0.7** (по умолчанию) - строгий (меньше ложных срабатываний)
- **0.65** - умеренный
- **0.5** - мягкий (больше новых аномалий)

```bash
# Изменить порог
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "log_file=@logs.txt" \
  -F "threshold=0.65"
```

---

## 🔍 Отладка

### Логи API

API выводит логи в консоль:

```
INFO:     Получен запрос на анализ: logs.txt
INFO:     Парсинг 1 файлов логов
INFO:     Распарсено 1000 строк логов
INFO:     Загружено 501 аномалий из словаря
INFO:     Запуск ML-анализа с порогом 0.7
INFO:     ML-анализ завершен: найдено 45 проблем
INFO:     Excel отчет создан: report.xlsx
```

### Проверка здоровья

```bash
curl http://localhost:8000/health
```

Если что-то не так, покажет статус каждого сервиса.

---

## 💡 Советы

1. **Первый запрос медленный** (~10-15 сек) - загружается ML-модель
2. **Последующие быстрые** (~2-5 сек)
3. **Максимальный размер файла** - ограничен только RAM сервера
4. **Excel формат** - точно такой же, как для защиты
5. **Swagger UI** (`/docs`) - лучший способ для тестирования

---

## 🐳 Опционально: Docker

Если хочешь запустить в Docker:

```bash
# Создай Dockerfile в api/
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]

# Запусти
docker build -t log-analyzer-api api/
docker run -p 8000:8000 log-analyzer-api
```

---

## ❓ FAQ

**Q: Это та же логика, что в боте?**  
A: Да, 100%. Твой код из `core/services/` используется и ботом, и API.

**Q: Excel файлы такие же, как для защиты?**  
A: Да, точно такие же. Формат не изменился.

**Q: Можно изменить threshold?**  
A: Да, передай параметр `threshold` при запросе.

**Q: Как добавить авторизацию?**  
A: Можно добавить JWT токены в FastAPI (если понадобится).

**Q: Можно использовать в продакшене?**  
A: Да, но лучше добавить:
  - Rate limiting
  - Авторизацию
  - Мониторинг
  - Reverse proxy (Nginx)

---

## 📞 Контакты

**Команда:** Black Lotus  
**Место:** 4-е на AtomicHack Hackathon 2025  
**Telegram бот:** @AtomicHackLogBot

---

**Ключевая идея:** API - это HTTP обертка вокруг **твоей логики**. Ничего не изменилось, просто теперь можно использовать через HTTP! 🚀

