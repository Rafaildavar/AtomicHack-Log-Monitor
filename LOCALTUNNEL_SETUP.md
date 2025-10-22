# 🌐 LocalTunnel Setup для Vercel

## Шаг 1: Запустить локальный туннель

```bash
# Туннель уже запущен на порте 8001
# Его URL будет выглядеть как: https://xxxxxxx-xxxx.loca.lt
```

## Шаг 2: Получить URL туннеля

При запуске `lt --port 8001` в консоли появится URL вида:
```
your url is: https://xxxxxxx-xxxx.loca.lt
```

## Шаг 3: Настроить Vercel

На Vercel в переменных окружения установи:
```
VITE_API_URL=https://xxxxxxx-xxxx.loca.lt
```

## Шаг 4: Задеплоить на Vercel

```bash
git push origin main
# Vercel автоматически задеплоит с новой переменной окружения
```

## ⚠️ Важно:

- **LocalTunnel URL меняется** при каждом запуске
- Туннель работает только пока запущен локально
- Для продакшена нужно задеплоить API на Railway/Render

## 🚀 Когда API на Railway будет готов:

Просто обнови `VITE_API_URL` на Railway URL в Vercel переменных.
