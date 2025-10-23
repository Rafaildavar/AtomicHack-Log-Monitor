# 📋 Итоговая сводка: Что сделано и как это работает

## 🎯 Главная задача

Создать **REST API** для функций анализа логов, написанных коллегой, чтобы их можно было:
1. Использовать в **Telegram боте** (как сейчас)
2. Использовать через **REST API** (для интеграции в другие системы)
3. Использовать в **других системах** (через API)

**Ключевое требование:** Генерация Excel отчетов должна остаться **точно такой же**, как для защиты на хакатоне.

---

## ✅ Что сделано

### 1. 📦 Core - Общий слой с логикой коллеги

Создана папка `core/` с **точной логикой коллеги** из бота:

```
core/
├── __init__.py
└── services/
    ├── __init__.py
    ├── ml_analyzer.py         # ML-анализ (ЛОГИКА КОЛЛЕГИ БЕЗ ИЗМЕНЕНИЙ)
    ├── log_parser.py          # Парсинг логов (ЛОГИКА КОЛЛЕГИ)
    └── report_generator.py    # Excel отчеты (ФОРМАТ ДЛЯ ЗАЩИТЫ)
```

#### 📄 ml_analyzer.py
**Что внутри:**
- Точная копия `src/bot/services/ml_log_analyzer.py`
- ML-модель: Sentence Transformers (all-MiniLM-L6-v2)
- Логика коллеги:
  - Semantic search через embeddings
  - Cosine similarity для сопоставления аномалий
  - Обработка новых аномалий (score > 0.5)
  - Точное совпадение ERROR с проблемами
  - Threshold: 0.7 (настраиваемый)

**Используется:**
- ✅ В боте: `src/bot/handlers/upload.py`
- ✅ В API: `api/main.py`
- 🔜 В других системах (через API)

#### 📄 log_parser.py
**Что внутри:**
- Адаптированная версия `src/bot/services/log_parser.py`
- Поддержка sync (для API) и async (для бота) режимов
- Логика коллеги:
  - Regex парсинг строк логов
  - Нормализация уровней (WARNING, ERROR)
  - Извлечение: datetime, level, source, text
  - Поддержка ZIP архивов
  - Обработка UTF-8 и Latin-1 кодировок

**Используется:**
- ✅ В боте: async версия
- ✅ В API: sync версия
- 🔜 В других системах (через API)

#### 📄 report_generator.py
**Что внутри:**
- Точная копия `src/bot/services/analysis_history.py` (метод `create_excel_report`)
- **Генерация Excel В ТОЧНОСТИ КАК ДЛЯ ЗАЩИТЫ:**
  - Колонки: `ID сценария`, `ID аномалии`, `ID проблемы`, `Файл с проблемой`, `№ строки`, `Строка из лога`
  - Форматирование: голубые заголовки (B4C7E7), центрирование текста
  - Ширина колонок: ID=12, Файл=20, Строка=80
  - Формат: `.xlsx` (OpenPyXL)

**Используется:**
- ✅ В боте: для генерации отчетов
- ✅ В API: для генерации отчетов
- 🔜 В веб-интерфейсе (скачивание через API)

---

### 2. 🌐 REST API (FastAPI)

Создан полноценный REST API:

```
api/
├── __init__.py
├── main.py              # FastAPI приложение
├── requirements.txt     # Зависимости
└── README.md           # Документация API
```

#### 📄 main.py - FastAPI приложение

**Основные эндпоинты:**

```python
# 1. Корневой эндпоинт
GET /
→ Информация о API, версия, команда

# 2. Health check
GET /health
→ Статус API, состояние ML-модели

# 3. ГЛАВНЫЙ: Анализ логов (использует логику коллеги)
POST /api/v1/analyze
→ Параметры:
   - log_file: файл с логами (.txt, .log, .zip)
   - anomalies_file: словарь аномалий (опционально)
   - threshold: порог ML (default: 0.7)
→ Возвращает:
   - JSON с результатами анализа
   - Ссылка на Excel отчет

# 4. Скачать Excel отчет (формат для защиты)
GET /api/v1/download/{filename}
→ Возвращает .xlsx файл

# 5. Дефолтный словарь
GET /api/v1/anomalies/default
→ Возвращает anomalies_problems.csv

# 6. Автодокументация (Swagger)
GET /docs
→ Интерактивная документация API
```

**Что происходит при вызове `/api/v1/analyze`:**

1. **Прием файла** - загружается файл с логами
2. **Извлечение** - если ZIP, извлекаются файлы (логика `LogParser`)
3. **Парсинг** - парсятся строки логов (логика `LogParser`)
4. **Загрузка словаря** - используется пользовательский или дефолтный
5. **ML-анализ** - запускается `MLLogAnalyzer.analyze_logs_with_ml()` (ЛОГИКА КОЛЛЕГИ)
6. **Генерация Excel** - создается отчет через `ReportGenerator` (ФОРМАТ ЗАЩИТЫ)
7. **Возврат результата** - JSON + ссылка на Excel

#### 📄 requirements.txt

```
fastapi==0.109.0          # Веб-фреймворк
uvicorn==0.27.0           # ASGI сервер
sentence-transformers==2.2.2  # ML-модель (как у коллеги)
pandas==2.2.0             # Обработка данных (как у коллеги)
torch==2.1.2              # ML backend (как у коллеги)
openpyxl==3.1.2           # Excel отчеты (как у коллеги)
```

---

## 🔄 Как это работает

### Схема архитектуры

```
┌────────────────────────────────────────────────────────┐
│                 ПОЛЬЗОВАТЕЛЬ                           │
└────┬───────────────────┬───────────────────────────────┘
     │                   │
     │ (текущий)         │ (новый)
     │                   │
┌────▼─────┐        ┌───▼────────┐
│ Telegram │        │  REST API  │
│   Bot    │        │ (FastAPI)  │
└────┬─────┘        └───┬────────┘
     │                   │
     │  Используют одну и ту же логику
     │                   │
     └──────────┬────────┘
                │
       ┌────────▼────────┐
       │  CORE SERVICES  │
       │ (Логика коллеги)│
       └────────┬────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼──────┐ ┌─▼────────┐ ┌▼────────────┐
│ML        │ │Log       │ │Report       │
│Analyzer  │ │Parser    │ │Generator    │
│(коллега) │ │(коллега) │ │(защита)     │
└──────────┘ └──────────┘ └─────────────┘
```

### Пример: Анализ логов через API

**Шаг 1: Пользователь отправляет запрос**

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "log_file=@logs.txt" \
  -F "threshold=0.7"
```

**Шаг 2: API принимает файл**

```python
# В api/main.py
@app.post("/api/v1/analyze")
async def analyze_logs(log_file: UploadFile, threshold: float = 0.7):
    # Сохраняем файл во временную директорию
    log_file_path = save_uploaded_file(log_file)
```

**Шаг 3: Парсинг логов (ЛОГИКА КОЛЛЕГИ)**

```python
# Импорт из core/
from core.services.log_parser import LogParser

log_parser = LogParser()
logs_df = log_parser.parse_log_files([log_file_path])
# Результат: DataFrame с колонками:
#   datetime, level, source, text, filename, line_number
```

**Шаг 4: ML-анализ (ЛОГИКА КОЛЛЕГИ)**

```python
# Импорт из core/
from core.services.ml_analyzer import MLLogAnalyzer

ml_analyzer = MLLogAnalyzer(similarity_threshold=threshold)
results_df = ml_analyzer.analyze_logs_with_ml(logs_df, anomalies_df)
# Результат: DataFrame с найденными проблемами:
#   ID аномалии, ID проблемы, Файл с проблемой, № строки, Строка из лога
```

**Шаг 5: Генерация Excel (ФОРМАТ ЗАЩИТЫ)**

```python
# Импорт из core/
from core.services.report_generator import ReportGenerator

report_generator = ReportGenerator()
excel_path = report_generator.create_excel_report(results_df)
# Результат: путь к .xlsx файлу с форматированием как для защиты
```

**Шаг 6: Возврат результата**

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
      "unique_anomalies": 12
    }
  },
  "results": [...],
  "excel_report": "/api/v1/download/report.xlsx"
}
```

---

## 🎯 Ключевые особенности

### 1. **Единая логика**

```
Telegram Bot  →  использует  →  core/services/
REST API      →  использует  →  core/services/
Другие системы →  используют  →  core/services/ (через API)
```

**Преимущества:**
- ✅ Одинаковые результаты везде
- ✅ Легко поддерживать (изменения в одном месте)
- ✅ Нет дублирования кода
- ✅ Логика коллеги не меняется

### 2. **Тот же формат Excel**

```python
# core/services/report_generator.py
def create_excel_report(analysis_results, output_path):
    # ТОЧНО ТА ЖЕ ЛОГИКА, что для защиты:
    
    # 1. Колонки в правильном порядке
    columns = ['ID сценария', 'ID аномалии', 'ID проблемы', 
               'Файл с проблемой', '№ строки', 'Строка из лога']
    
    # 2. Голубые заголовки (B4C7E7)
    header_fill = PatternFill(start_color='B4C7E7', ...)
    
    # 3. Центрирование текста
    alignment = Alignment(horizontal='center', vertical='center')
    
    # 4. Фиксированная ширина колонок
    ws.column_dimensions['F'].width = 80  # Строка из лога
```

**Результат:** Excel файлы **идентичны** тем, что были для защиты.

### 3. **Автодокументация**

FastAPI автоматически генерирует:
- **Swagger UI** (http://localhost:8000/docs) - интерактивная документация
- **ReDoc** (http://localhost:8000/redoc) - красивая документация
- **OpenAPI схема** - для генерации клиентов

### 4. **Готовность к интеграции**

API можно использовать из:

**Python:**
```python
import requests
response = requests.post('http://api/analyze', files={'log_file': f})
```

**JavaScript:**
```javascript
fetch('http://api/analyze', {method: 'POST', body: formData})
```

**cURL:**
```bash
curl -X POST -F "log_file=@logs.txt" http://api/analyze
```

---

## 📊 Примеры использования

### 1. Через Swagger UI (браузер)

1. Запустить API: `cd api && python main.py`
2. Открыть: http://localhost:8000/docs
3. Выбрать `POST /api/v1/analyze`
4. Нажать "Try it out"
5. Загрузить файл
6. Получить результат + скачать Excel

### 2. Через Python скрипт

```python
import requests

# Анализ
with open('logs.txt', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/analyze',
        files={'log_file': f}
    )

result = response.json()
print(f"Найдено проблем: {result['analysis']['ml_results']['total_problems']}")

# Скачать Excel
excel_url = f"http://localhost:8000{result['excel_report']}"
excel_response = requests.get(excel_url)
with open('report.xlsx', 'wb') as f:
    f.write(excel_response.content)
```

### 3. Интеграция в другую систему

```python
# В вашей системе мониторинга
from my_monitoring_system import get_logs
import requests

# Получаем логи
logs = get_logs(last_hour=True)

# Отправляем на анализ
response = requests.post(
    'http://atomichack-api:8000/api/v1/analyze',
    files={'log_file': logs}
)

# Обрабатываем результаты
if response.json()['analysis']['ml_results']['total_problems'] > 0:
    send_alert("Обнаружены аномалии!")
```

---

## 📁 Структура файлов

```
Хакатон МИФИ/
│
├── core/                         # 🔥 НОВОЕ: Общая логика
│   ├── __init__.py
│   └── services/
│       ├── __init__.py
│       ├── ml_analyzer.py        # Логика коллеги
│       ├── log_parser.py         # Логика коллеги
│       └── report_generator.py   # Формат защиты
│
├── api/                          # 🔥 НОВОЕ: REST API
│   ├── __init__.py
│   ├── main.py                   # FastAPI приложение
│   ├── requirements.txt
│   └── README.md
│
├── src/bot/                      # СУЩЕСТВУЮЩИЙ: Telegram бот
│   └── ...                       # (теперь может использовать core/)
│
├── ARCHITECTURE.md               # 🔥 НОВОЕ: Описание архитектуры
├── QUICKSTART.md                 # 🔥 НОВОЕ: Быстрый старт
├── SUMMARY.md                    # 🔥 НОВОЕ: Этот файл
└── test_api.py                   # 🔥 НОВОЕ: Тестовый скрипт
```

---

## 🚀 Что дальше

### ✅ Выполнено

1. ✅ **Core-слой** - логика коллеги вынесена в отдельный модуль
2. ✅ **REST API** - FastAPI с автодокументацией
3. ✅ **Excel отчеты** - тот же формат, что для защиты
4. ✅ **Документация** - README, ARCHITECTURE, QUICKSTART

### 🔜 В планах (TODO)

1. **Другие системы** (через API)
   - Красивый UI для загрузки файлов
   - Интерактивные таблицы и графики
   - История анализов

2. **Доработка бота**
   - История анализов пользователя
   - Генерация API ключей
   - Настройка threshold через меню

3. **Docker & CI/CD**
   - Docker контейнеры для всех сервисов
   - GitHub Actions для автоматического деплоя
   - Деплой на Railway/Render

---

## 🎓 Резюме

### Что сделано

Создана **единая архитектура** с общим core-слоем, которая:
- 📦 Использует **точную логику коллеги** из `core/services/`
- 🤖 Работает в **Telegram боте** (как раньше)
- 🌐 Работает через **REST API** (для интеграции)
- 📊 Генерирует **Excel в том же формате**, что для защиты
- 📖 Имеет **автодокументацию** (Swagger UI)
- 🔌 Готова к **интеграции** в другие системы

### Как это работает

1. **Логика коллеги** находится в `core/services/`
2. **Бот и API** импортируют функции из `core/`
3. **Результаты** идентичны везде (одна логика)
4. **Excel отчеты** генерируются в том же формате
5. **API** предоставляет HTTP интерфейс для анализа

### Ключевое

✅ **Логика коллеги НЕ изменена** - точная копия в `core/`  
✅ **Формат Excel НЕ изменен** - такой же, как для защиты  
✅ **Единообразие** - бот и API используют один код  
✅ **Готово к расширению** - легко добавить новые интерфейсы  

---

**Команда Black Lotus** 🌸  
4-е место на AtomicHack Hackathon 2025

