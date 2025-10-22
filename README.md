# AtomicHack Log Monitor

Интеллектуальная система для анализа логов на базе машинного обучения.

## 🚀 Deployment

### Frontend на Vercel

1. Подключи репо к Vercel
2. Перейди в **Settings → Environment Variables**
3. Добавь переменную:
   - **Name:** `VITE_API_URL`
   - **Value:** `https://твой-api-url` (URL backend API)
4. Нажми Redeploy

### Backend на Railway / Render

API развертывается отдельно на Railway или Render с использованием Python.

## 📝 Локальная разработка

```bash
# Frontend
cd web
VITE_API_URL=http://localhost:8001 npm run dev

# Backend (в отдельном терминале)
cd api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001
```

## 🔗 API Configuration

Frontend ищет переменную `VITE_API_URL`:
- **Локально:** `http://localhost:8001`
- **На Vercel:** URL твоего публичного API (Railway/Render/т.д.)
