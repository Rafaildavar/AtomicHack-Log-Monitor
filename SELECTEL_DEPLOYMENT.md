# 🚀 Деплой API на Selectel (ВМ + Python)

## 📋 Шаг 1: Создание виртуальной машины

1. **Зайдите на https://selectel.ru/**
   - Зарегистрируйтесь или войдите в аккаунт
   - Пополните баланс (минимум ~500₽ на месяц)

2. **Создайте виртуальную машину:**
   - Перейдите в раздел **"Облачная платформа"** → **"Серверы"**
   - Нажмите **"Создать сервер"**
   
   **Параметры:**
   - **Регион:** Москва (или ближайший к вам)
   - **ОС:** Ubuntu 22.04 LTS
   - **Конфигурация:** 
     - vCPU: 2
     - RAM: 4 GB (минимум, лучше 8 GB для ML моделей)
     - Диск: 50 GB SSD
   - **Сеть:** Публичный IP (обязательно!)
   - **SSH ключ:** Добавьте свой публичный SSH ключ (если нет - создадим)

3. **Сохраните данные:**
   - IP адрес сервера (например: `123.45.67.89`)
   - Имя пользователя (обычно `root` или `ubuntu`)

---

## 🔑 Шаг 2: Подключение к серверу

### Если у вас НЕТ SSH ключа:

```bash
# Создайте SSH ключ на вашем Mac
ssh-keygen -t ed25519 -C "your_email@example.com"

# Нажмите Enter 3 раза (сохранит в ~/.ssh/id_ed25519)

# Скопируйте публичный ключ
cat ~/.ssh/id_ed25519.pub

# Вставьте этот ключ в Selectel при создании ВМ
```

### Подключение к серверу:

```bash
# Замените IP на ваш
ssh root@123.45.67.89

# Если пользователь ubuntu:
ssh ubuntu@123.45.67.89
```

---

## 🛠 Шаг 3: Настройка сервера

После подключения к серверу выполните команды:

```bash
# 1. Обновление системы
sudo apt update && sudo apt upgrade -y

# 2. Установка необходимых пакетов
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx certbot python3-certbot-nginx

# 3. Создание директории для приложения
sudo mkdir -p /opt/app
sudo chown $USER:$USER /opt/app
cd /opt/app

# 4. Клонирование проекта
git clone https://github.com/ВАШ_ЮЗЕРНЕЙМ/ВАШ_РЕПО.git .

# Если нужна авторизация, используйте Personal Access Token:
# git clone https://ВАШ_TOKEN@github.com/ВАШ_ЮЗЕРНЕЙМ/ВАШ_РЕПО.git .

# 5. Создание виртуального окружения
python3.11 -m venv venv
source venv/bin/activate

# 6. Установка зависимостей
pip install --upgrade pip
pip install -r api/requirements.txt

# 7. Тест запуска (Ctrl+C для остановки)
PYTHONPATH=/opt/app uvicorn api.main:app --host 0.0.0.0 --port 8001
```

Если всё работает - переходите к следующему шагу!

---

## 🔄 Шаг 4: Создание systemd сервиса

На сервере создайте файл сервиса:

```bash
sudo nano /etc/systemd/system/fastapi.service
```

Вставьте содержимое (замените `ubuntu` на вашего пользователя, если нужно):

```ini
[Unit]
Description=FastAPI Log Analyzer
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/app
Environment="PYTHONPATH=/opt/app"
Environment="PATH=/opt/app/venv/bin"
ExecStart=/opt/app/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8001 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

Запустите сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi
sudo systemctl status fastapi
```

Должно быть: **`active (running)`** зеленым цветом!

---

## 🌐 Шаг 5: Настройка Nginx

Создайте конфиг Nginx:

```bash
sudo nano /etc/nginx/sites-available/fastapi
```

Вставьте (замените `123.45.67.89` на ваш IP):

```nginx
server {
    listen 80;
    server_name 123.45.67.89;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }
}
```

Активируйте конфиг:

```bash
sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## ✅ Шаг 6: Проверка работы

На вашем Mac:

```bash
# Замените IP на ваш
curl http://123.45.67.89/api/v1/health

# Должно вернуть: {"status":"healthy"}
```

Или откройте в браузере: `http://123.45.67.89/docs` - должна открыться Swagger документация!

---

## 🔒 Шаг 7: Настройка CORS

На сервере откройте файл:

```bash
nano /opt/app/api/main.py
```

Найдите секцию CORS и добавьте ваш Vercel домен:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://ваш-домен.vercel.app",  # ← Добавьте ваш домен Vercel
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Перезапустите сервис:

```bash
sudo systemctl restart fastapi
```

---

## 🌍 Шаг 8: Обновление Vercel

1. **Зайдите на https://vercel.com/**
2. Откройте ваш проект
3. Перейдите в **Settings** → **Environment Variables**
4. Добавьте/обновите переменную:
   - **Name:** `VITE_API_URL`
   - **Value:** `http://123.45.67.89` (ваш IP)
   - **Environments:** Production, Preview, Development

5. **Redeploy** проект:
   - Перейдите в **Deployments**
   - Нажмите на последний деплой → **"..."** → **"Redeploy"**

---

## 🎉 Готово!

Теперь ваш API работает на Selectel, а фронтенд на Vercel подключается к нему!

---

## 🔧 Полезные команды

```bash
# Просмотр логов API
sudo journalctl -u fastapi -f

# Перезапуск API
sudo systemctl restart fastapi

# Проверка статуса
sudo systemctl status fastapi

# Обновление кода
cd /opt/app
git pull
source venv/bin/activate
pip install -r api/requirements.txt
sudo systemctl restart fastapi
```

---

## 🆘 Если что-то не работает

1. **Проверьте логи:**
   ```bash
   sudo journalctl -u fastapi -n 100
   ```

2. **Проверьте порты:**
   ```bash
   sudo netstat -tulpn | grep 8001
   ```

3. **Проверьте firewall:**
   ```bash
   sudo ufw status
   # Если активен, откройте порты:
   sudo ufw allow 80
   sudo ufw allow 443
   ```

4. **Проверьте Nginx:**
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

---

## 💰 Стоимость

- **ВМ 2 vCPU / 4 GB RAM:** ~500-700₽/месяц
- **ВМ 2 vCPU / 8 GB RAM:** ~900-1200₽/месяц

Намного дешевле чем Render.com ($7 = ~700₽, но там меньше ресурсов)!


