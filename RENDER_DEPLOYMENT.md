# 🚀 Деплой на Render.com (Python)

## Шаг 1: Регистрация и подготовка

1. Зайдите на https://render.com/
2. Зарегистрируйтесь через GitHub (это упростит подключение репозитория)
3. Подключите ваш репозиторий: https://github.com/Rafaildavar/AtomicHack-Log-Monitor

## Шаг 2: Создание Web Service

1. В Dashboard нажмите **"New +"** → **"Web Service"**
2. Выберите репозиторий `AtomicHack-Log-Monitor`
3. Настройте параметры:

### Основные настройки:
- **Name**: `atomichack-log-monitor-api`
- **Region**: `Frankfurt (EU Central)` (ближайший к России)
- **Branch**: `main`
- **Root Directory**: оставьте пустым
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r api/requirements.txt`
- **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### План (выберите один):
- **Free**: Засыпает после 15 минут неактивности (для теста)
- **Starter ($7/мес)**: Не засыпает, 512 MB RAM ⭐ **Рекомендую для хакатона**
- **Standard ($25/мес)**: 2 GB RAM, лучше для ML моделей

**Рекомендация**: Начните с **Starter** ($7/мес). Этого хватит на 3 дня, и можно отменить подписку после хакатона.

### Переменные окружения (Environment Variables):
Render автоматически установит `PORT`, дополнительно можно добавить:
- `PYTHONUNBUFFERED`: `1` (для вывода логов в реальном времени)
- `PYTHON_VERSION`: `3.11.0` (если нужна конкретная версия)

## Шаг 3: Деплой

1. Нажмите **"Create Web Service"**
2. Render начнёт установку зависимостей (это займёт 5-10 минут)
3. Следите за логами сборки в реальном времени

### Что происходит при деплое:
1. Render клонирует ваш репозиторий
2. Устанавливает Python 3.11
3. Выполняет `pip install -r api/requirements.txt` (устанавливает все зависимости, включая PyTorch и ML модели)
4. Запускает `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

## Шаг 4: Получение URL

После успешного деплоя:
1. Ваш API будет доступен на: `https://atomichack-log-monitor-api.onrender.com`
2. Проверьте health endpoint: `https://atomichack-log-monitor-api.onrender.com/health`

## Шаг 5: Обновление Vercel

1. Зайдите в настройки проекта на Vercel
2. **Settings** → **Environment Variables**
3. Обновите или создайте переменную:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://atomichack-log-monitor-api.onrender.com` (ваш URL с Render)
4. Нажмите **"Redeploy"** чтобы пересобрать фронтенд с новым URL

## Шаг 6: Проверка

1. Откройте https://atomichaclogmonitor.vercel.app/
2. Попробуйте загрузить файлы и запустить анализ
3. Всё должно работать! 🎉

## 💰 Стоимость

- **Starter план**: $7/мес
- **Можно отменить после хакатона**: Settings → Billing → Cancel Subscription
- **Пропорциональный возврат**: Render вернёт деньги за неиспользованное время

## ⚠️ Важные замечания

1. **Первый запуск**: API может загружаться 30-60 секунд (загрузка ML модели sentence-transformers)
2. **Логи**: Доступны в реальном времени в Dashboard → Logs
3. **Автодеплой**: При каждом push в `main` Render автоматически пересобирает приложение
4. **Размер**: Установка всех зависимостей займёт ~2 GB (PyTorch, transformers, pandas и т.д.)

## 🐛 Если что-то пошло не так

### Проблема: "Build failed"
- Проверьте логи сборки в Render Dashboard
- Убедитесь, что `api/requirements.txt` существует
- Проверьте, что все зависимости корректны

### Проблема: "Service unavailable" или 503
- Подождите 1-2 минуты - ML модель загружается при старте
- Проверьте логи работы API в разделе Logs
- Убедитесь, что выбран план Starter или выше (Free может не хватить памяти)

### Проблема: "Out of memory"
- Upgrade на Standard план ($25/мес) с 2 GB RAM
- Или используйте более лёгкую ML модель

### Проблема: Vercel не подключается к API
- Убедитесь, что `VITE_API_URL` правильно указан в Vercel
- Проверьте CORS настройки в `api/main.py` (уже настроено)
- Попробуйте открыть API URL напрямую в браузере

## 📊 Мониторинг

В Render Dashboard вы можете:
- Смотреть логи в реальном времени
- Видеть использование CPU и памяти
- Перезапускать сервис при необходимости
- Откатываться на предыдущие версии

---

**Готово!** Теперь ваше приложение полностью в облаке и доступно 24/7! 🚀

## 🎯 Быстрый чеклист

- [ ] Зарегистрировались на Render.com
- [ ] Создали Web Service с Python runtime
- [ ] Указали Build Command: `pip install -r api/requirements.txt`
- [ ] Указали Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- [ ] Выбрали план Starter ($7/мес)
- [ ] Дождались успешного деплоя
- [ ] Получили URL вида `https://xxx.onrender.com`
- [ ] Обновили `VITE_API_URL` на Vercel
- [ ] Сделали Redeploy на Vercel
- [ ] Проверили работу на https://atomichaclogmonitor.vercel.app/

Удачи! 🍀
