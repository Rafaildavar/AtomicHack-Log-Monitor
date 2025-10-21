# Архитектура AtomicHack Log Monitor 2.0

## 🎯 Концепция

Проект развивается в **экосистему** с тремя точками доступа:
1. **Telegram Bot** - для быстрого анализа через мессенджер
2. **REST API** - для интеграции в другие системы
3. **Web Interface** - для удобного анализа через браузер

**Ключевая особенность:** Все три интерфейса используют **одинаковую логику анализа** (написанную коллегой), что гарантирует единообразие результатов.

## 📊 Структура проекта

```
AtomicHack-Log-Monitor/
│
├── core/                          # 🔥 ОБЩАЯ ЛОГИКА (используется всеми)
│   ├── services/
│   │   ├── ml_analyzer.py        # ML-анализ (логика коллеги БЕЗ ИЗМЕНЕНИЙ)
│   │   ├── log_parser.py         # Парсинг логов (логика коллеги)
│   │   └── report_generator.py   # Excel отчеты (формат для защиты)
│   ├── models/
│   └── utils/
│
├── bot/                           # Telegram бот (существующий)
│   ├── src/bot/
│   │   ├── handlers/
│   │   ├── services/             # Теперь использует core/
│   │   └── main.py
│   └── requirements.txt
│
├── api/                           # REST API (новый)
│   ├── main.py                   # FastAPI приложение
│   ├── routes/
│   ├── models/
│   ├── requirements.txt
│   └── README.md
│
├── web/                           # Веб-интерфейс (в разработке)
│   ├── frontend/                 # React/Vue
│   │   ├── src/
│   │   ├── public/
│   │   └── package.json
│   └── backend/                  # Опционально (может использовать API напрямую)
│
├── docker/
│   ├── docker-compose.yml        # Все сервисы вместе
│   ├── Dockerfile.api
│   ├── Dockerfile.bot
│   └── Dockerfile.web
│
├── docs/
│   ├── API.md
│   ├── INTEGRATION.md
│   └── DEPLOYMENT.md
│
└── tests/
    ├── test_ml_analyzer.py
    ├── test_log_parser.py
    └── test_api.py
```

## 🔄 Поток данных

```
┌─────────────────────────────────────────────────────────────┐
│                    ПОЛЬЗОВАТЕЛЬ                              │
└────┬─────────────────┬─────────────────┬────────────────────┘
     │                 │                 │
     │                 │                 │
┌────▼────┐      ┌─────▼─────┐      ┌──▼──────┐
│Telegram │      │    API    │      │   Web   │
│  Bot    │      │ (FastAPI) │      │  (React)│
└────┬────┘      └─────┬─────┘      └──┬──────┘
     │                 │                 │
     └─────────────────┼─────────────────┘
                       │
              ┌────────▼────────┐
              │   CORE SERVICES │
              │  (Логика коллеги)│
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼───┐   ┌────▼────┐   ┌───▼──────┐
    │ML      │   │Log      │   │Report    │
    │Analyzer│   │Parser   │   │Generator │
    └────────┘   └─────────┘   └──────────┘
```

## 🎨 Core Services (Общая логика)

### 1. MLLogAnalyzer

**Файл:** `core/services/ml_analyzer.py`

**Описание:** ML-анализ логов с использованием Sentence Transformers.

**Логика коллеги:**
- ✅ Semantic search через embeddings
- ✅ Cosine similarity для сопоставления аномалий
- ✅ Обработка новых аномалий (score > 0.5)
- ✅ Точное совпадение ERROR с проблемами

**Используется в:**
- Telegram Bot: `src/bot/handlers/upload.py`
- API: `api/main.py` → POST `/api/v1/analyze`
- Web: будет использовать API

### 2. LogParser

**Файл:** `core/services/log_parser.py`

**Описание:** Парсинг логов с поддержкой различных форматов.

**Логика коллеги:**
- ✅ Regex парсинг строк логов
- ✅ Нормализация уровней (WARNING, ERROR)
- ✅ Извлечение datetime, source, text
- ✅ Поддержка ZIP архивов

**Используется в:**
- Telegram Bot: `src/bot/services/log_parser.py` (async версия)
- API: `core/services/log_parser.py` (sync версия)
- Web: через API

### 3. ReportGenerator

**Файл:** `core/services/report_generator.py`

**Описание:** Создание Excel отчетов в формате для защиты хакатона.

**Формат отчета (БЕЗ ИЗМЕНЕНИЙ):**
- Колонки: `ID сценария`, `ID аномалии`, `ID проблемы`, `Файл с проблемой`, `№ строки`, `Строка из лога`
- Форматирование: голубые заголовки, центрирование, фиксированная ширина колонок
- Формат: `.xlsx` (OpenPyXL)

**Используется в:**
- Telegram Bot: `src/bot/services/analysis_history.py`
- API: `api/main.py` → генерация Excel
- Web: скачивание через API

## 🔌 API Endpoints

### Базовые

- `GET /` - Информация о API
- `GET /health` - Health check
- `GET /docs` - Swagger UI (автодокументация)

### Анализ логов

- `POST /api/v1/analyze` - Анализ логов (логика коллеги)
  - Параметры: `log_file`, `anomalies_file` (optional), `threshold`
  - Возвращает: JSON с результатами + ссылка на Excel

- `GET /api/v1/download/{filename}` - Скачать Excel отчет (формат для защиты)

### Словари

- `GET /api/v1/anomalies/default` - Получить дефолтный словарь

## 🤖 Telegram Bot

**Текущий функционал:**
- ✅ Загрузка логов (txt, log, zip)
- ✅ ML-анализ (логика коллеги)
- ✅ Генерация Excel отчетов
- ✅ Поддержка дефолтного словаря

**Планируемые улучшения (TODO #3):**
- История анализов
- Персональные API ключи
- Настройка threshold через меню
- Уведомления о завершении анализа
- Мультиязычность

## 🌐 Web Interface (TODO #2)

**Технологии:**
- Frontend: React + TypeScript + TailwindCSS
- API клиент: Axios + React Query
- Графики: Chart.js

**Страницы:**
1. **Главная** - описание, демо, команда
2. **Анализ** - drag&drop, выбор словаря, настройки
3. **Результаты** - таблица, графики, экспорт
4. **История** - сохраненные анализы (требует БД)
5. **API Docs** - интерактивная документация

## 🐳 Docker

**Файлы:**
- `docker-compose.yml` - оркестрация всех сервисов
- `Dockerfile.api` - API контейнер
- `Dockerfile.bot` - Bot контейнер  
- `Dockerfile.web` - Web контейнер

**Запуск всей системы:**

```bash
docker-compose up
```

Сервисы:
- API: http://localhost:8000
- Web: http://localhost:3000
- Bot: работает в фоне

## 📦 Зависимости

**Общие (для всех):**
- sentence-transformers==2.2.2
- pandas==2.2.0
- torch==2.1.2
- openpyxl==3.1.2

**API специфичные:**
- fastapi==0.109.0
- uvicorn==0.27.0

**Bot специфичные:**
- aiogram==3.3.0
- aiofiles==23.2.1

## 🔐 Безопасность

**API:**
- CORS настроен для конкретных доменов
- Rate limiting (планируется)
- JWT авторизация (планируется)
- Валидация файлов

**Bot:**
- Очистка временных файлов
- Ограничение размера файлов (20MB)
- Логирование всех операций

## 📈 Масштабирование

**Текущая архитектура:**
- Монолитный API (один процесс)
- Бот в одном процессе
- Web статика

**Планы:**
- Redis для кэширования
- Celery для асинхронных задач
- PostgreSQL для истории и пользователей
- Nginx как reverse proxy
- Horizontal scaling для API

## 🧪 Тестирование

**Юнит-тесты:**
- `tests/test_ml_analyzer.py` - тесты ML-логики
- `tests/test_log_parser.py` - тесты парсера
- `tests/test_report_generator.py` - тесты генерации отчетов

**Интеграционные тесты:**
- `tests/test_api.py` - тесты API endpoints
- `tests/test_bot.py` - тесты бота

**E2E тесты:**
- Полный цикл: загрузка → анализ → отчет

## 🚀 Deployment

**Development:**
```bash
# API
cd api && python main.py

# Bot
cd src/bot && python -m main

# Web
cd web/frontend && npm run dev
```

**Production:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 👥 Команда

**Black Lotus**
- 4-е место на AtomicHack Hackathon 2025
- Telegram Bot: @AtomicHackLogBot

## 📄 Лицензия

MIT

---

**Ключевой принцип:** Вся логика анализа написана коллегой и находится в `core/`. Любые изменения в алгоритме делаются ТОЛЬКО в `core/`, и автоматически применяются везде (бот, API, web).

