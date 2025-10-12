# AtomicHack Log Monitor

**Команда:** Black Lotus 
**Кейс:** ИИ-анализатор журналов событий приложений

Система автоматического анализа логов с использованием ML для выявления аномалий и их связей с критическими проблемами в инфраструктуре.

---

https://disk.yandex.ru/client/disk/ХАКАТОН%20АТОМИКХАК%2012.10.2025 ссылка на яндекс диск где находятся: Презентация, скринкаст, тизер, и ссылка на решение(тг бот)

---

## Описание решения

Система анализирует логи приложений и инфраструктуры, используя ML-модель для семантического поиска аномалий (WARNING) и автоматического сопоставления их с критическими проблемами (ERROR). Результаты представляются в виде структурированного Excel отчета с полной трассировкой от аномалии до проблемы.

---

## Архитектура системы

### 1. Telegram Bot (интерфейс)
- Прием файлов: `txt`, `log`, `csv`, `zip` (до 20MB)
- Асинхронная обработка запросов
- Автоматическая валидация входных данных
- Отправка Excel отчетов пользователю

### 2. ML-модуль обработки логов (ядро системы)

#### 2.1 Парсинг и предобработка
```python
# Извлечение структурированных данных из логов
for line in log_file:
    # Формат: datetime level source: text
    # Пример: 2024-10-11 WARNING CPU0: Temperature critical
    
    parts = line.split(' ', 2)
    dt, level, rest = parts[0], parts[1], parts[2]
    
    # Извлечение source (CPU0, Memory, Disk и т.д.)
    if ':' in rest:
        source, text = rest.split(':', 1)
    
    # Нормализация уровня
    level = 'WARNING' if 'WARNING' in level.upper() else 'ERROR'
```

**Результат:** Структурированный DataFrame со столбцами:
- `datetime` - временная метка
- `level` - уровень (WARNING/ERROR)
- `source` - источник сообщения
- `text` - текст проблемы (очищенный от метаданных)
- `full_line` - полная строка для вывода
- `filename` - имя файла
- `line_number` - номер строки

#### 2.2 ML-анализ с Sentence Transformers

**Модель:** `all-MiniLM-L6-v2`
- Размерность эмбеддингов: 384
- Нормализация: L2-normalized
- Метрика: Косинусное сходство

```python
# Загрузка модели
model = SentenceTransformer("all-MiniLM-L6-v2")

# Создание эмбеддингов для известных аномалий из словаря
known_anomalies = ["CPU0: Temperature critical", 
                   "RAID array degraded", 
                   "Memory ECC error detected", ...]
anomaly_embeddings = model.encode(known_anomalies, normalize_embeddings=True)

# Анализ каждой WARNING строки из логов
for warning in warnings_df.iterrows():
    # Получаем эмбеддинг для текста WARNING
    text_embedding = model.encode(warning["text"], normalize_embeddings=True)
    
    # Вычисляем семантическое сходство со всеми известными аномалиями
    cosine_scores = util.cos_sim(text_embedding, anomaly_embeddings)[0]
    best_idx = cosine_scores.argmax().item()
    best_score = cosine_scores[best_idx].item()
    
    # Порог уверенности: 0.7
    if best_score >= 0.7:
        # Нашли похожую аномалию!
        matched_anomaly = anomalies_dict.iloc[best_idx]
    else:
        # Низкая уверенность - записываем None
        results.append({'ID аномалии': None, 'ID проблемы': None, ...})
```

**Преимущества семантического поиска:**
- Устойчивость к вариациям текста
- Находит похожие по смыслу сообщения, даже если формулировка отличается
- Не требует точного совпадения строк

#### 2.3 Сопоставление аномалий с проблемами

**Логика цепочки:**
```
WARNING (лог) 
    ↓ [ML: семантический поиск, score >= 0.7]
Аномалия (словарь)
    ↓ [Lookup: по таблице связей]
ID проблемы
    ↓ [Exact match: точное совпадение текста]
ERROR (лог)
```

```python
# Шаг 1: WARNING → Аномалия (уже найдено через ML)
matched_anomaly = anomalies_dict.iloc[best_idx]
anomaly_text = matched_anomaly["Аномалия"]

# Шаг 2: Аномалия → Проблемы (из словаря связей)
related_problems = anomalies_problems_df[
    anomalies_problems_df["Аномалия"] == anomaly_text
]

# Шаг 3: Проблема → ERROR (точное совпадение)
for problem in related_problems:
    problem_text = problem["Проблема"]
    
    # Ищем ERROR строки с точным совпадением текста проблемы
    error_rows = logs_df[
        (logs_df["level"] == "ERROR") &
        (logs_df["text"].isin([problem_text]))
    ]
    
    # Для каждого найденного ERROR записываем результат
    for error in error_rows:
        results.append({
            'ID аномалии': problem['ID аномалии'],
            'ID проблемы': problem['ID проблемы'],
            'Файл с проблемой': error['filename'],
            '№ строки': error['line_number'],
            'Строка из лога': error['full_line']
        })
```

**Пример работы:**
```
Входные данные:
  WARNING: "CPU0: Temperature above safe threshold"

ML обработка:
  Эмбеддинг → косинусное сходство → best_match = "CPU0: Temperature critical"
  Score: 0.89 (выше 0.7 - принимаем)

Словарь аномалий:
  ID аномалии: 9
  Аномалия: "CPU0: Temperature critical"
  ID проблемы: 2
  Проблема: "CPU0: Core temperature above threshold"

Поиск ERROR:
  Ищем в логах: level == "ERROR" AND text == "CPU0: Core temperature above threshold"
  Найдено: system.log, строка 142

Результат:
  ✓ ID аномалии: 9
  ✓ ID проблемы: 2
  ✓ Файл: system.log
  ✓ Строка: 142
  ✓ Полная строка: "2024-10-11 ERROR CPU0: Core temperature above threshold"
```

#### 2.4 Обработка множественных сценариев

```python
# Автоматическое обнаружение сценариев в ZIP-архиве
for root, dirs, files in os.walk(extract_dir):
    if 'anomalies_problems.csv' in files:
        scenario_name = os.path.basename(os.path.dirname(root))
        scenarios.append((scenario_name, anomalies_csv_path))

# Если словарь не найден - используем встроенный
if not scenarios:
    default_dict = "src/bot/services/anomalies_problems.csv"
    scenarios.append(("default", default_dict))

# Обработка каждого сценария независимо
for scenario_name, anomalies_file in scenarios:
    # Загрузка словаря
    anomalies_dict = pd.read_csv(anomalies_file, sep=';')
    
    # Поиск логов для сценария
    logs = find_logs_for_scenario(scenario_name, extract_dir)
    
    # ML анализ
    results = ml_analyzer.analyze_logs_with_ml(logs, anomalies_dict)
    
    # Добавляем ID сценария
    results['Сценарий'] = scenario_name
```

**ID сценариев:**
- Назначаются автоматически в порядке обработки
- Первый обработанный сценарий → ID = 1
- Второй → ID = 2, и т.д.

### 3. Генерация Excel отчетов

```python
def create_excel_report(analysis_results):
    # Шаг 1: Назначение ID сценариям
    scenario_id_mapping = {}
    current_id = 1
    
    for result in analysis_results:
        scenario_name = result['Сценарий']
        if scenario_name not in scenario_id_mapping:
            scenario_id_mapping[scenario_name] = current_id
            current_id += 1
    
    # Шаг 2: Формирование данных отчета
    report_data = []
    for anomaly in results:
        report_data.append({
            'ID сценария': scenario_id_mapping[anomaly['Сценарий']],
            'ID аномалии': anomaly['ID аномалии'],
            'ID проблемы': anomaly['ID проблемы'],
            'Файл с проблемой': anomaly['Файл с проблемой'],
            '№ строки': anomaly['№ строки'],
            'Строка из лога': anomaly['Строка из лога']
        })
    
    # Шаг 3: Создание DataFrame и сохранение
    df = pd.DataFrame(report_data)
    df.to_excel(output_path, index=False, engine='openpyxl')
    
    # Шаг 4: Форматирование
    wb = load_workbook(output_path)
    ws = wb.active
    
    # Заголовки: голубой фон (#B4C7E7), жирный шрифт
    header_fill = PatternFill(start_color='B4C7E7', 
                              end_color='B4C7E7', 
                              fill_type='solid')
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Все ячейки: выравнивание по центру, перенос текста
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(horizontal='center', 
                                      vertical='center', 
                                      wrap_text=True)
    
    # Ширина колонок (в символах)
    ws.column_dimensions['A'].width = 12  # ID сценария
    ws.column_dimensions['B'].width = 12  # ID аномалии
    ws.column_dimensions['C'].width = 12  # ID проблемы
    ws.column_dimensions['D'].width = 20  # Файл
    ws.column_dimensions['E'].width = 10  # № строки
    ws.column_dimensions['F'].width = 80  # Строка из лога (широкая!)
    
    wb.save(output_path)
```

**Формат итогового Excel:**

| ID сценария | ID аномалии | ID проблемы | Файл с проблемой | № строки | Строка из лога |
|:-----------:|:-----------:|:-----------:|:----------------:|:--------:|:---------------|
| 1 | 9 | 2 | system.log | 142 | 2024-10-11 ERROR CPU0: Core temperature above threshold |
| 1 | 17 | 3 | system.log | 358 | 2024-10-11 ERROR Memory ECC error detected |
| 2 | 25 | 4 | power.log | 89 | 2024-10-11 ERROR PSU voltage out of range |

---

## Технический стек

### Основные библиотеки
- **Python** 3.13+
- **aiogram** 3.22.0 - Telegram Bot API
- **sentence-transformers** 5.1.1 - ML модели для NLP
- **PyTorch** 2.8.0 - backend для трансформеров
- **pandas** 2.3.3 - обработка табличных данных
- **openpyxl** 3.1.5 - создание Excel файлов

### ML компоненты
- **Модель:** all-MiniLM-L6-v2 (384-размерные эмбеддинги)
- **Метрика:** Косинусное сходство
- **Порог уверенности:** 0.7
- **Нормализация:** L2-normalized embeddings

### Производительность
- **Скорость анализа:** ~30 сек на 1.5 млн строк
- **ML инференс:** ~0.1 сек на WARNING
- **Макс. размер файла:** 20MB (ограничение Telegram Bot API)
- **Обработка:** параллельная для множественных сценариев

---

## Структура проекта

```
src/
├── bot/
│   ├── handlers/
│   │   ├── upload.py          # Обработка загрузки файлов, ML анализ
│   │   ├── menu.py            # Меню и команды бота
│   │   └── start.py           # Стартовый хендлер
│   ├── services/
│   │   ├── ml_log_analyzer.py      # ML-анализ с трансформерами (ЯДРО)
│   │   ├── analysis_history.py     # Генерация Excel отчетов
│   │   ├── log_parser.py           # Скачивание файлов из Telegram
│   │   └── anomalies_problems.csv  # Встроенный словарь (501 аномалия)
│   ├── keyboards/
│   │   └── main.py            # Клавиатуры для бота
│   ├── config.py              # Конфигурация (токены, настройки)
│   └── main.py                # Точка входа (запуск бота)
└── chain_with_transformer.py  # Оригинальный ML модуль (reference)
```

---

## Быстрый старт

### 1. Установка зависимостей
   ```bash
cd /path/to/project
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

### 2. Настройка
Создайте файл `.env`:
   ```env
BOT_TOKEN=your_telegram_bot_token_here
   ```

### 3. Запуск
   ```bash
   python -m src.bot.main
   ```

### 4. Использование

**Вариант 1: С собственным словарем**
```
Структура ZIP:
├── ValidationCase 1/
│   ├── anomalies_problems.csv  <- Ваш словарь
│   ├── system.log
│   └── app.log
```

**Вариант 2: Без словаря (используется встроенный)**
```
Просто отправьте:
- system.log (одиночный файл)
- logs.zip (архив с логами, без CSV)
```

**Результат:**
- Excel файл с найденными проблемами
- Статистика: кол-во сценариев, проблем, аномалий

---

## Формат входных данных

### Словарь аномалий (CSV, разделитель `;`)
```csv
ID аномалии;Аномалия;ID проблемы;Проблема
9;CPU0: Temperature critical;2;CPU0: Core temperature above threshold
17;ECC single-bit error;3;Memory ECC error detected
25;PSU1 voltage drop;4;PSU voltage out of range
```

**Важно:**
- Один словарь может содержать несколько проблем для одной аномалии
- ID аномалии уникальны в пределах словаря
- ID проблемы - это идентификатор класса проблем

### Логи (TXT/LOG)
```
2024-10-11 WARNING CPU0: Temperature above safe threshold
2024-10-11 ERROR CPU0: Core temperature above threshold
2024-10-11 INFO System: Normal operation resumed
```

**Формат:** `datetime level source: message`

---

## Команды бота

- **`/start`** - приветствие и главное меню
- **Кнопка "Загрузить логи"** - начать анализ
- **Кнопка "Справка"** - информация о боте

---

## Особенности реализации

### 1. Дефолтный словарь аномалий
- Встроенный словарь: `src/bot/services/anomalies_problems.csv`
- 501 аномалия, 50 типов проблем
- Используется автоматически, если пользователь не предоставил свой

### 2. Нормализация данных
- Автоматическое извлечение source из логов
- Нормализация уровней (ERROR, WARNING)
- Очистка текста от метаданных

### 3. Обработка ошибок
- Низкая уверенность ML (<0.7) → запись с None
- Нет найденных ERROR → пустой отчет
- Превышен размер файла → информативное сообщение

### 4. Масштабируемость
- Поддержка множественных сценариев в одном ZIP
- Уникальные имена файлов отчетов (timestamp)
- Автоматическая очистка временных файлов

---

## Контакты

**Команда:** Black Lotus  
**Хакатон:** AtomicHack  
**GitHub:** https://github.com/Rafaildavar/AtomicHack-Log-Monitor

---

## Лицензия

Проект создан в рамках хакатона AtomicHack.
Условия использования определяются организаторами.
