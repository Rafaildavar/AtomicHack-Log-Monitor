# Docker Deployment Guide

## Быстрый старт с Docker

### 1. Подготовка

Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

Отредактируйте `.env` и добавьте ваш токен бота:
```env
BOT_TOKEN=your_telegram_bot_token
LOG_LEVEL=INFO
AIOHTTP_CLIENT_TIMEOUT=600
```

### 2. Сборка и запуск

#### Вариант A: Docker Compose (рекомендуется)
```bash
docker-compose up -d
```

#### Вариант B: Чистый Docker
```bash
# Сборка образа
docker build -t atomichack-log-monitor .

# Запуск контейнера
docker run -d \
  --name atomichack-bot \
  --env-file .env \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/reports:/app/reports \
  atomichack-log-monitor
```

### 3. Управление контейнером

```bash
# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Проверка статуса
docker-compose ps
```

### 4. Обновление

```bash
# Пересборка после изменений
docker-compose up -d --build
```

## Системные требования

- Docker 20.10+
- Docker Compose 2.0+
- Минимум 2GB RAM
- Минимум 2GB свободного места на диске

## Структура томов (volumes)

- `./downloads` → `/app/downloads` - временные файлы загрузок
- `./reports` → `/app/reports` - сгенерированные Excel отчеты
- `./src/bot/services/anomalies_problems.csv` → встроенный словарь аномалий

## Порты

- **8080** - зарезервирован для webhook (если потребуется)

## Ограничения ресурсов

Настроены в `docker-compose.yml`:
- CPU: 1-2 ядра
- RAM: 2-4 GB

## Логирование

Логи контейнера:
```bash
docker logs atomichack-log-monitor -f
```

## Интеграция в существующую инфраструктуру

### Подключение к внешней сети
```yaml
networks:
  default:
    external: true
    name: your-existing-network
```

### Использование внешних томов
```yaml
volumes:
  reports:
    external: true
    name: shared-reports-volume
```

### Настройка прокси
```yaml
environment:
  - HTTP_PROXY=http://proxy:8080
  - HTTPS_PROXY=http://proxy:8080
```

## Troubleshooting

### Бот не запускается
1. Проверьте токен в `.env`
2. Проверьте логи: `docker-compose logs`
3. Проверьте доступность Telegram API

### Нехватка памяти
Увеличьте лимиты в `docker-compose.yml`:
```yaml
resources:
  limits:
    memory: 8G
```

### Проблемы с ML моделью
При первом запуске модель скачивается (500MB). Убедитесь в наличии интернета и места на диске.

## Production Deployment

Для production рекомендуется:

1. Использовать orchestrator (Kubernetes, Docker Swarm)
2. Настроить мониторинг (Prometheus + Grafana)
3. Подключить centralized logging (ELK Stack)
4. Настроить health checks
5. Использовать secrets management

Пример для Kubernetes доступен в `k8s/` директории (если требуется).

