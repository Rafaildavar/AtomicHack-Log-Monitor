# 🚀 Деплой на Render.com

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
- **Runtime**: `Docker`
- **Dockerfile Path**: `Dockerfile` (должен определиться автоматически)

### План:
- **Free**: Засыпает после 15 минут неактивности (для теста)
- **Starter ($7/мес)**: Не засыпает, 512 MB RAM (рекомендую для хакатона)
- **Standard ($25/мес)**: 2 GB RAM, лучше для ML моделей

**Рекомендация**: Начните с **Starter** ($7/мес). Этого хватит на 3 дня, и можно отменить подписку после хакатона.

### Переменные окружения (Environment Variables):
Добавьте (если нужны):
- `PORT`: `8001` (обычно Render сам устанавливает)
- `PYTHONUNBUFFERED`: `1`

## Шаг 3: Деплой

1. Нажмите **"Create Web Service"**
2. Render начнёт сборку Docker образа (это займёт 10-15 минут)
3. Следите за логами сборки в реальном времени

## Шаг 4: Получение URL

После успешного деплоя:
1. Ваш API будет доступен на: `https://atomichack-log-monitor-api.onrender.com`
2. Проверьте health endpoint: `https://atomichack-log-monitor-api.onrender.com/health`

## Шаг 5: Обновление Vercel

1. Зайдите в настройки проекта на Vercel
2. **Settings** → **Environment Variables**
3. Обновите или создайте переменную:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://atomichack-log-monitor-api.onrender.com`
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

1. **Первый запуск**: API может загружаться 30-60 секунд (загрузка ML модели)
2. **Логи**: Доступны в реальном времени в Dashboard → Logs
3. **Автодеплой**: При каждом push в `main` Render автоматически пересобирает приложение

## 🐛 Если что-то пошло не так

1. Проверьте логи сборки в Render Dashboard
2. Проверьте логи работы API в разделе Logs
3. Убедитесь, что Dockerfile корректный (он уже настроен)

---

**Готово!** Теперь ваше приложение полностью в облаке и доступно 24/7! 🚀
