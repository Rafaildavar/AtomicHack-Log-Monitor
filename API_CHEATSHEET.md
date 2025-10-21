# 🚀 API - Шпаргалка для коллеги

## Запуск за 3 шага

```bash
# 1. Установить
pip install -r api/requirements.txt

# 2. Запустить
cd api && python main.py

# 3. Тест
открой http://localhost:8000/docs
```

---

## Главный endpoint

```bash
# Анализ логов
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "log_file=@logs.txt" \
  -F "threshold=0.7"
```

**Ответ:**
```json
{
  "status": "success",
  "analysis": {
    "ml_results": {
      "total_problems": 45,
      "unique_anomalies": 12
    }
  },
  "excel_report": "/api/v1/download/report.xlsx"
}
```

---

## Из Python

```python
import requests

with open('logs.txt', 'rb') as f:
    r = requests.post(
        'http://localhost:8000/api/v1/analyze',
        files={'log_file': f}
    )

print(r.json()['analysis']['ml_results']['total_problems'])
```

---

## Как это работает

```
API получает файл
    ↓
Твой LogParser парсит
    ↓
Твой MLLogAnalyzer анализирует
    ↓
Твой ReportGenerator создает Excel
    ↓
API возвращает результат
```

**Вся твоя логика в `core/services/` - без изменений!**

---

## Все endpoints

```bash
# Анализ
POST /api/v1/analyze

# Скачать Excel
GET /api/v1/download/{filename}

# Дефолтный словарь
GET /api/v1/anomalies/default

# Health check
GET /health

# Документация
GET /docs
```

---

## Важно

✅ Твоя логика БЕЗ изменений  
✅ Excel формат как для защиты  
✅ Swagger UI для тестов: `/docs`  
✅ Первый запрос ~15 сек (загрузка модели)  
✅ Остальные ~3 сек  

---

**Вопросы?** Открывай `API_GUIDE.md` - там полное описание! 🎯

