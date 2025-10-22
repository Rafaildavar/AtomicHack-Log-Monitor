# Деплой API на Render

## Шаг 1: Подготовка

Убедись, что все изменения закомичены:
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Шаг 2: Создание сервиса на Render

1. Зайди на https://render.com
2. Нажми **"New"** → **"Web Service"**
3. Подключи GitHub репозиторий
4. Заполни параметры:
   - **Name**: `atomichack-api`
   - **Region**: `Frankfurt` (или ближайший к тебе)
   - **Branch**: `main`
   - **Runtime**: `Python 3.11`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

## Шаг 3: Переменные окружения (если нужны)

Если нужны ENV переменные, добавь их на странице "Environment":
```
PYTHON_VERSION=3.11
```

## Шаг 4: Деплой

1. Нажми **"Create Web Service"**
2. Ждёшь ~5-10 минут (ML модель загружается)
3. Когда статус станет "Live" ✅ — готово!

## Шаг 5: Получение URL API

После деплоя Render выдаст тебе URL типа:
```
https://atomichack-api-xxxxx.onrender.com
```

## Шаг 6: Обновление фронта

Обнови `web/.env.production` с новым URL:
```
VITE_API_URL=https://atomichack-api-xxxxx.onrender.com
```

Или оставь без переменных, и фронт будет автоматически подключаться к Render API.

## Проверка

```bash
curl https://atomichack-api-xxxxx.onrender.com/
```

Должен вернуть:
```json
{
  "message": "AtomicHack Log Monitor API",
  "version": "1.0.0",
  "team": "Black Lotus",
  "docs": "/docs",
  "status": "running"
}
```

## Swagger Docs

После деплоя документация будет доступна:
```
https://atomichack-api-xxxxx.onrender.com/docs
```

## Особенности Free Plan на Render

- ✅ Бесплатно
- ⚠️ Спит после 15 минут неактивности
- ⏳ Холодный старт ~30 сек (ML модель загружается)
- 🔄 Автоматический деплой при push в main

## Если ML модель не загружается

Если видишь ошибки на Render, проверь логи и попробуй:

1. Увеличить RAM на платном плане
2. Оптимизировать модель (использовать более лёгкую)
3. Закешировать модель в Docker образе

## Кэширование для ускорения

Если хочешь быстрого запуска, можно добавить Docker:

1. Создай `Dockerfile`
2. Деплой как "Docker" вместо "Python"
3. Модель будет скачана один раз при сборке образа

Удачи с деплоем! 🚀
