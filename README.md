# Atomic Log Monitor - Система анализа логов

Комплексная система для анализа логов с поддержкой машинного обучения и мониторинга в реальном времени.

## Возможности

### Обычный анализ логов
- Загрузка и анализ файлов логов (TXT, LOG, ZIP)
- Обнаружение аномалий с помощью машинного обучения
- Генерация интерактивных графиков и отчетов
- Детальная статистика по типам событий
- Экспорт результатов в различные форматы

### Мониторинг в реальном времени
- Потоковый анализ логов через WebSocket
- Обнаружение аномалий в реальном времени
- Мониторинг изменений файлов с помощью watchdog
- Интерактивная статистика и уведомления
- Поддержка больших файлов с оптимизированной обработкой

### Машинное обучение
- Использование Sentence Transformers для анализа текста
- Автоматическое обнаружение аномалий в логах
- Сравнение с базой известных проблем
- Настраиваемые пороги чувствительности

## Архитектура

### Backend (API)
- **FastAPI** - высокопроизводительный веб-фреймворк
- **WebSocket** - для реал-тайм коммуникации
- **Pandas** - обработка данных
- **Sentence Transformers** - ML анализ
- **Watchdog** - мониторинг файловой системы
- **Plotly** - генерация графиков

### Frontend (Web)
- **React + TypeScript** - современный интерфейс
- **Vite** - быстрая сборка
- **Tailwind CSS** - стилизация
- **WebSocket Client** - реал-тайм обновления

### Docker
- Полная контейнеризация API
- Docker Compose для оркестрации
- Изолированная среда выполнения

## Установка и запуск

### Локальная разработка

#### Backend (API)
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (Web)
```bash
cd web
npm install
npm run dev
```

### Docker развертывание

#### API
```bash
cd api
docker build -t log-monitor-api .
docker run -p 8000:8000 log-monitor-api
```

#### Полная система с Docker Compose
```bash
cd api
docker-compose up -d
```

## Использование

### Обычный анализ
1. Откройте главную страницу
2. Загрузите файл лога (TXT, LOG, ZIP)
3. Настройте параметры анализа
4. Запустите анализ
5. Просмотрите результаты и графики

### Реал-тайм мониторинг
1. Перейдите на страницу "Реал-тайм"
2. Загрузите файл лога
3. Запустите мониторинг
4. Наблюдайте за обновлениями в реальном времени

## API Endpoints

### Основные
- `POST /api/v1/analyze` - анализ логов
- `GET /api/v1/timeline/{session_id}` - получение временной шкалы
- `GET /api/v1/sessions` - список сессий

### Реал-тайм мониторинг
- `POST /api/v1/stream/start` - запуск мониторинга
- `WebSocket /api/v1/stream/{session_id}` - WebSocket соединение
- `POST /api/v1/stream/stop/{session_id}` - остановка мониторинга
- `GET /api/v1/stream/status/{session_id}` - статус мониторинга

## Конфигурация

### Переменные окружения
```bash
# API настройки
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# ML настройки
ML_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
ANOMALY_THRESHOLD=0.7

# Файловая система
UPLOAD_DIR=uploads
MAX_FILE_SIZE=100MB
```

### Docker настройки
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
    environment:
      - API_HOST=0.0.0.0
      - API_PORT=8000
```

## Структура проекта

```
├── api/                    # Backend API
│   ├── main.py            # Основной файл API
│   ├── requirements.txt   # Python зависимости
│   ├── Dockerfile        # Docker конфигурация
│   └── docker-compose.yml # Docker Compose
├── web/                   # Frontend приложение
│   ├── src/
│   │   ├── components/    # React компоненты
│   │   ├── pages/        # Страницы
│   │   └── api/          # API клиент
│   ├── package.json      # Node.js зависимости
│   └── vite.config.ts    # Vite конфигурация
├── docs/                  # Документация
└── README.md             # Этот файл
```

## Технические детали

### Обработка файлов
- Поддержка TXT, LOG, ZIP форматов
- Автоматическое извлечение из архивов
- Потоковая обработка больших файлов
- Валидация и очистка данных

### ML анализ
- Предобученные модели Sentence Transformers
- Векторное представление текста
- Косинусное сходство для поиска аномалий
- Настраиваемые пороги детекции

### Производительность
- Батчевая обработка для больших файлов
- Асинхронная обработка через asyncio
- Оптимизированные алгоритмы парсинга
- Кэширование результатов

## Разработка

### Требования
- Python 3.8+
- Node.js 16+
- Docker (опционально)

### Установка зависимостей
```bash
# Backend
cd api
pip install -r requirements.txt

# Frontend
cd web
npm install
```

### Запуск в режиме разработки
```bash
# Backend
cd api
uvicorn main:app --reload

# Frontend
cd web
npm run dev
```

### Тестирование
```bash
# API тесты
cd api
pytest

# Frontend тесты
cd web
npm test
```

## Развертывание

### Production
```bash
# Сборка и запуск
docker-compose -f docker-compose.prod.yml up -d

# Проверка статуса
docker-compose ps

# Логи
docker-compose logs -f
```

### Мониторинг
- Health check: `GET /health`
- Метрики: `GET /metrics`
- Логи: `docker-compose logs -f api`

## Безопасность

- Валидация входных данных
- Ограничения размера файлов
- Санитизация путей файлов
- CORS настройки
- Rate limiting

## Производительность

- Асинхронная обработка
- Потоковая загрузка файлов
- Оптимизированные алгоритмы ML
- Кэширование результатов
- Батчевая обработка

## Поддержка

### Логи и отладка
```bash
# API логи
docker-compose logs api

# Frontend логи
npm run dev -- --debug

# Системные логи
tail -f /var/log/syslog
```

### Мониторинг ресурсов
```bash
# Использование памяти
docker stats

# Дисковое пространство
df -h

# Сетевые соединения
netstat -tulpn
```

## Лицензия

MIT License - см. файл LICENSE для деталей.

## Авторы

Команда Atomic Black Lotus - Хакатон МИФИ 2024

## Контакты

- GitHub: [Atomic_black_lotus_191](https://github.com/hackathonsrus/Atomic_black_lotus_191)
- Email: rafail.davar@rambler.ru
- Документация: [Wiki](https://github.com/hackathonsrus/Atomic_black_lotus_191/wiki)