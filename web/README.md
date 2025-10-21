# AtomicHack Log Monitor - Web Interface

Современный веб-интерфейс для анализа логов с использованием ML.

## Технологии

- **React 18** + **TypeScript**
- **Vite** - быстрая сборка
- **TailwindCSS** - современный styling
- **Framer Motion** - плавные анимации
- **React Query** - управление состоянием API
- **React Router** - маршрутизация
- **Recharts** - графики и визуализация
- **Lucide React** - иконки

## Установка

```bash
npm install
```

## Запуск

### Development
```bash
npm run dev
```

Откроется на http://localhost:5173

### Production Build
```bash
npm run build
npm run preview
```

## Конфигурация

Создайте `.env` файл:

```env
VITE_API_URL=http://localhost:8000
```

## Структура проекта

```
src/
├── components/
│   ├── layout/          # Header, Footer
│   ├── upload/          # FileUploader, ProgressBar, SettingsPanel
│   ├── results/         # ResultsTable, Charts, Stats
│   ├── real-time/       # LiveMonitor, WebSocket
│   └── history/         # AnalysisHistory, CompareResults
├── pages/
│   ├── Home.tsx         # Landing page
│   ├── Analyze.tsx      # Upload & analyze page
│   ├── Results.tsx      # Results display
│   ├── Dashboard.tsx    # Real-time dashboard
│   ├── History.tsx      # Analysis history
│   ├── Documentation.tsx
│   └── About.tsx
├── api/
│   └── client.ts        # API client
├── hooks/
│   ├── useAnalyze.ts    # Analysis hook
│   └── useWebSocket.ts  # WebSocket hook
├── lib/
│   └── utils.ts         # Utility functions
├── App.tsx
└── main.tsx
```

## Страницы

- `/` - Landing page с описанием проекта
- `/analyze` - Загрузка и анализ логов
- `/results` - Результаты анализа с графиками
- `/dashboard` - Real-time мониторинг
- `/history` - История анализов
- `/docs` - API документация
- `/about` - О проекте и команде

## Фичи

### ✅ Реализовано

- Современный UI/UX с dark theme
- Drag & Drop загрузка файлов
- Настройка ML threshold
- Интеграция с FastAPI backend
- Анимации и transitions
- Responsive design

### 🚧 В разработке

- Real-time WebSocket updates
- Интерактивные графики (Recharts)
- История анализов
- Сравнение результатов
- Экспорт в разные форматы

## API Integration

Приложение работает с FastAPI backend:

```typescript
import { analyzeLogsAPI } from './api/client';

// Анализ логов
const result = await analyzeLogsAPI(logFile, anomaliesFile, 0.7);
```

## Deploy

### Vercel (рекомендуется)

```bash
npm install -g vercel
vercel --prod
```

### Build для других платформ

```bash
npm run build
# Dist папка готова для деплоя
```

## Команда

**Black Lotus** - 4-е место на AtomicHack Hackathon 2025

## Лицензия

MIT
