# 🚀 Деплой API на Railway

## Почему Railway?

- **Свободный тариф:** 5$/месяц кредитов (достаточно для запуска)
- **Память:** 2GB RAM (хватит для ML модели)
- **Просто:** 1-клик деплой из GitHub
- **Быстро:** автоматический CD/CI

---

## ✅ Шаг 1: Подготовка к деплою

### 1.1 Проверь, что все файлы готовы

```bash
cd /Users/remi/Desktop/GUAP/Хакатон\ МИФИ
ls -la
```

Должны быть:
- `api/` - папка с исходным кодом API
- `requirements.txt` - зависимости (в корне или в api/)
- `Procfile` - конфигурация для Railway

### 1.2 Убедись что `Procfile` существует и правильный

```bash
cat Procfile
```

Должно быть:
```
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

Если нет, создай его:
```bash
echo "web: uvicorn api.main:app --host 0.0.0.0 --port \$PORT" > Procfile
```

---

## 🔑 Шаг 2: Создай аккаунт Railway

1. Перейди на **https://railway.app**
2. Нажми **"Sign Up"** → выбери **"GitHub"**
3. Авторизуйся с GitHub аккаунтом
4. Подтверди эмейл

---

## 📦 Шаг 3: Создай новый проект

1. На главной Railway нажми **"+ New Project"**
2. Выбери **"Deploy from GitHub repo"**
3. Подключи репозиторий `AtomicHack-Log-Monitor`
4. Выбери **branch:** `main`

---

## ⚙️ Шаг 4: Настрой сервис

### 4.1 После выбора репо Railway спросит "Deploy Now?"

**НЕ спеши нажимать! Сначала нужно настроить:**

1. Нажми на **"Variables"** или **"Settings"**
2. В разделе **"Service"** установи:
   - **Name:** `atomichack-api`
   - **Region:** `Frankfurt` (или `North America`, как удобно)

### 4.2 Настрой переменные окружения (если нужны)

Если используешь `.env` - добавь переменные:

1. Нажми **"Variables"**
2. Добавь строки (если используются):
   ```
   PYTHON_VERSION=3.11
   PORT=8000
   ```

### 4.3 Настрой путь к requirements

1. Нажми **"Settings"**
2. Установи **"Root Directory":** `.` (если requirements в корне) или `api` (если в папке api)

---

## 🚀 Шаг 5: Запусти деплой

1. Нажми **"Deploy Now"**
2. Railway автоматически:
   - Загружает код
   - Устанавливает зависимости (`pip install -r requirements.txt`)
   - Запускает Uvicorn сервер

---

## 📊 Шаг 6: Мониторь логи деплоя

1. В Railway откроется **"Logs"** вкладка
2. Жди сообщение:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```
3. Если видишь ошибку - изучи логи, найди проблему

**Частые ошибки:**
- `ModuleNotFoundError` → проверь requirements.txt
- `Port already in use` → Railway сама управляет портом
- `Out of memory` → увели RAM на платном плане

---

## 🌐 Шаг 7: Получи URL API

1. После успешного деплоя нажми на сервис
2. Вверху найди **"Deployments"** → выбери последний
3. Скопируй **URL** (выглядит так: `https://atomichack-api-production.up.railway.app`)

**Проверь что API работает:**
```bash
curl https://atomichack-api-production.up.railway.app/health
```

Должен быть ответ (JSON или текст)

---

## 🔗 Шаг 8: Добавь URL на Vercel

1. Перейди на **vercel.com** → твой проект
2. **Settings** → **Environment Variables**
3. Добавь новую переменную:
   ```
   Name:  VITE_API_URL
   Value: https://atomichack-api-production.up.railway.app
   ```
4. Нажми **"Save"** → **"Redeploy"**

---

## ✨ Готово!

Теперь:
- ✅ Frontend на Vercel (`https://atomichaclogmonitor.vercel.app`)
- ✅ Backend на Railway (`https://atomichack-api-production.up.railway.app`)
- ✅ Фронтенд подключен к бэкенду через `VITE_API_URL`

**Тестируй анализ:**
1. Открой https://atomichaclogmonitor.vercel.app/analyze
2. Загрузи файл логов
3. Нажми "Начать анализ"
4. Должно работать! 🎉

---

## 🐛 Если что-то не работает

### API не запускается?
```bash
# Проверь логи в Railway Dashboard
# Ищи ошибку и исправляй в коде
```

### Frontend не может подключиться к API?
- Проверь что `VITE_API_URL` установлена на Vercel
- Убедись что URL правильный (скопируй из Railway)
- Проверь CORS (должен быть включен в api/main.py)

### Медленная загрузка?
- Railway free tier имеет ограничения
- Можно обновить на Starter план ($5/месяц)

---

## 💡 Полезные ссылки

- **Railway Dashboard:** https://railway.app/dashboard
- **Railway Docs:** https://docs.railway.app
- **Vercel Dashboard:** https://vercel.com/dashboard

---

## 📝 Команды для локального тестирования (перед деплоем)

```bash
# 1. Установи зависимости
cd /Users/remi/Desktop/GUAP/Хакатон\ МИФИ/api
pip install -r requirements.txt

# 2. Запусти локально
uvicorn main:app --host 0.0.0.0 --port 8001

# 3. Проверь что работает
curl http://localhost:8001/health

# 4. Если работает - готово к деплою!
```

---

**Успеха! 🚀 Если есть вопросы - спрашивай!**
