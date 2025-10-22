"""FastAPI приложение для анализа логов.

Использует те же функции анализа коллеги, что и Telegram бот.
Генерирует Excel отчеты в том же формате, что и для защиты.
"""

import logging
import os
import tempfile
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import plotly.graph_objects as go

# Импортируем логику коллеги из core
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.services.ml_analyzer import MLLogAnalyzer
from core.services.log_parser import LogParser
from core.services.report_generator import ReportGenerator

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI(
    title="AtomicHack Log Monitor API",
    description="API для ML-анализа логов. Использует ту же логику, что и Telegram бот.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware для веб-интерфейса
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем сервисы (логика коллеги)
ml_analyzer = MLLogAnalyzer(similarity_threshold=0.7)
log_parser = LogParser()
report_generator = ReportGenerator()

# Создаем директорию для сохранения отчетов
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

# Загружаем ML модель один раз при старте (для быстрых анализов)
logger.info("⏳ Загрузка ML модели при старте API...")
ml_analyzer._load_model()
logger.info("✅ ML модель загружена и готова к анализам")


async def _save_upload_file(upload_file: UploadFile, destination_path: str) -> str:
    """
    Сохраняет загруженный файл на диск по частям, чтобы не занимать много памяти.
    Возвращает путь к сохраненному файлу.
    """
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    # Читаем и пишем по 1 МБ
    chunk_size_bytes = 1024 * 1024
    with open(destination_path, 'wb') as out_file:
        while True:
            chunk = await upload_file.read(chunk_size_bytes)
            if not chunk:
                break
            out_file.write(chunk)
    # Сбрасываем указатель, если файл понадобится повторно читать
    try:
        await upload_file.seek(0)
    except Exception:
        pass
    return destination_path


def generate_log_visualization(logs_df: pd.DataFrame) -> str:
    """
    Генерирует интерактивный HTML график распределения логов по времени.
    
    Args:
        logs_df: DataFrame с логами (columns: datetime, level, text, filename, line_number)
    
    Returns:
        HTML строка с графиком
    """
    try:
        # Подготовляем данные
        df = logs_df.copy()
        
        # Убедимся что у нас есть нужные колонки
        if 'datetime' not in df.columns or 'level' not in df.columns:
            logger.warning("Не хватает колонок для графика, используем пустой датафрейм")
            return "<div>Недостаточно данных для графика</div>"
        
        # Преобразуем datetime в нужный формат
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        df = df.dropna(subset=['datetime'])
        
        if df.empty:
            return "<div>Нет валидных данных для построения графика</div>"
        
        # Считаем количество логов по уровню
        level_counts = df['level'].value_counts().to_dict()
        
        # Определяем порядок и цвета
        level_order = ["INFO", "WARNING", "ERROR"]
        color_map = {
            "INFO": "#87CEEB",      # Light sky blue
            "WARNING": "#FFD700",    # Gold
            "ERROR": "#FF6347"       # Tomato
        }
        
        # Фильтруем только известные уровни
        df = df[df['level'].isin(level_order)]
        
        if df.empty:
            return "<div>Нет данных в известных уровнях логирования</div>"
        
        # Для очень больших наборов данных уменьшим выборку, чтобы не раздувать ответ
        max_points = 20000
        if len(df) > max_points:
            df = df.sample(n=max_points, random_state=42)

        # Создаем интерактивный scatter график
        fig = go.Figure()
        
        for level in level_order:
            level_data = df[df['level'] == level]
            if not level_data.empty:
                count = len(level_data)
                fig.add_trace(go.Scatter(
                    x=level_data['datetime'],
                    y=[level] * count,
                    mode='markers',
                    name=f"{level} ({count})",
                    marker=dict(
                        size=10,
                        color=color_map.get(level, "#999999"),
                        opacity=0.8,
                        line=dict(width=1, color="white")
                    ),
                    text=level_data['text'].astype(str),
                    hovertemplate='<b>%{y}</b><br>Время: %{x}<br>Сообщение: %{text}<extra></extra>'
                ))
        
        # Обновляем layout
        fig.update_layout(
            title="📊 Распределение логов по времени",
            xaxis_title="Время",
            yaxis_title="Уровень логирования",
            template="plotly_dark",
            height=400,
            hovermode='closest',
            yaxis=dict(categoryorder="array", categoryarray=level_order),
            plot_bgcolor="#0a0e27",
            paper_bgcolor="#0a0e27",
            font=dict(color="white", family="Arial, sans-serif")
        )
        
        # Возвращаем HTML
        html = fig.to_html(include_plotlyjs='cdn', config={'responsive': True})
        return html
        
    except Exception as e:
        logger.error(f"Ошибка при генерации графика: {e}")
        return f"<div style='color: red;'>Ошибка при генерации графика: {str(e)}</div>"


def generate_anomaly_graph(results_df: pd.DataFrame, anomalies_df: pd.DataFrame) -> str:
    """
    Генерирует интерактивный граф связей между аномалиями и проблемами.
    
    Args:
        results_df: DataFrame с результатами анализа
        anomalies_df: DataFrame со словарем аномалий
    
    Returns:
        HTML строка с интерактивным графом
    """
    try:
        import networkx as nx
        from pyvis.network import Network
        import tempfile
        
        if results_df.empty:
            return "<div>Нет аномалий для построения графа</div>"
        
        # Создаем граф
        G = nx.Graph()
        
        # Берем уникальные пары аномалия-проблема
        for _, row in results_df.iterrows():
            anom_id = int(row.get('ID аномалии', -1))
            prob_id = int(row.get('ID проблемы', -1))
            
            if anom_id == -1 or prob_id == -1:
                continue
            
            # Получаем текст аномалии и проблемы из словаря
            try:
                anom_matches = anomalies_df[anomalies_df['ID аномалии'].astype(int) == anom_id]
                prob_matches = anomalies_df[anomalies_df['ID проблемы'].astype(int) == prob_id]
                
                anom_text = anom_matches['Аномалия'].values[0] if len(anom_matches) > 0 else 'Unknown'
                prob_text = prob_matches['Проблема'].values[0] if len(prob_matches) > 0 else 'Unknown'
            except Exception:
                anom_text = 'Unknown'
                prob_text = 'Unknown'
            
            anom_label = f"Anom {anom_id}: {str(anom_text)[:30]}..."
            prob_label = f"Prob {prob_id}: {str(prob_text)[:30]}..."
            
            # Добавляем узлы и ребра
            G.add_node(anom_label, node_type="anomaly")
            G.add_node(prob_label, node_type="problem")
            G.add_edge(anom_label, prob_label)
        
        # Создаем визуализацию PyVis
        net = Network(
            height="500px",
            width="100%",
            bgcolor="#0a0e27",
            font_color="white",
            directed=False
        )
        
        net.from_nx(G)
        
        # Настройки внешнего вида
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -2000,
              "centralGravity": 0.3,
              "springLength": 150,
              "springConstant": 0.04
            }
          },
          "nodes": {
            "font": {"size": 16, "face": "Arial"},
            "scaling": {"min": 20, "max": 40}
          },
          "edges": {
            "color": {"color": "#00D4FF", "opacity": 0.6},
            "smooth": true
          }
        }
        """)
        
        # Сохраняем временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, dir=REPORTS_DIR) as f:
            temp_path = f.name
        
        # Сохраняем граф
        net.save_graph(temp_path)
        
        # Читаем HTML
        with open(temp_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Очищаем файл
        try:
            os.remove(temp_path)
        except:
            pass
        
        return html
        
    except ImportError:
        logger.error("Ошибка: networkx или pyvis не установлены")
        return "<div style='color: orange;'>GraphX libraries not available</div>"
    except Exception as e:
        logger.error(f"Ошибка при генерации графа: {e}")
        return f"<div style='color: red;'>Ошибка при генерации графа: {str(e)}</div>"


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "AtomicHack Log Monitor API",
        "version": "1.0.0",
        "team": "Black Lotus",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья API."""
    return {
        "status": "healthy",
        "ml_model": "loaded" if ml_analyzer.model is not None else "not_loaded",
        "services": {
            "ml_analyzer": "ready",
            "log_parser": "ready",
            "report_generator": "ready"
        }
    }


@app.post("/api/v1/analyze")
async def analyze_logs(
    log_file: UploadFile = File(..., description="Файл с логами (.txt, .log, .zip)"),
    anomalies_file: Optional[UploadFile] = File(None, description="Словарь аномалий (anomalies_problems.csv)"),
    threshold: str = Form("0.7")
):
    """
    Анализирует логи с использованием ML (логика коллеги).
    
    **Использует те же функции анализа, что и Telegram бот.**
    
    Args:
        log_file: Файл с логами (txt, log или zip)
        anomalies_file: Опциональный словарь аномалий (если не указан, используется дефолтный)
        threshold: Порог similarity для ML-модели (0.0-1.0)
    
    Returns:
        JSON с результатами анализа и ссылкой на Excel отчет
    """
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Преобразуем threshold из строки в число
        try:
            threshold_float = float(threshold)
            # Убедимся, что threshold в допустимом диапазоне
            threshold_float = max(0.0, min(1.0, threshold_float))
        except (ValueError, TypeError):
            threshold_float = 0.7
            logger.warning(f"Неверное значение threshold: {threshold}, использую дефолтное 0.7")
        
        logger.info(f"Получен запрос на анализ: {log_file.filename}")
        logger.info(f"🎯 Используемый порог схожести: {threshold_float}")
        
        # Сохраняем загруженный файл с логами (поштучно, чтобы избежать OOM)
        log_file_path = os.path.join(temp_dir, log_file.filename)
        await _save_upload_file(log_file, log_file_path)
        
        # Определяем файлы с логами
        if log_file.filename.endswith('.zip'):
            logger.info("Извлекаем ZIP архив")
            log_files = log_parser.extract_zip(log_file_path, temp_dir)
            # Фильтруем только лог-файлы (не CSV)
            log_files = [f for f in log_files if not f.endswith('anomalies_problems.csv')]
        else:
            log_files = [log_file_path]
        
        # Парсим логи (логика коллеги)
        logger.info(f"Парсинг {len(log_files)} файлов логов")
        logs_df = log_parser.parse_log_files(log_files)
        
        if logs_df.empty:
            raise HTTPException(status_code=400, detail="Не удалось распарсить логи. Проверьте формат файла.")
        
        logger.info(f"Распарсено {len(logs_df)} строк логов")
        
        # Базовый анализ
        basic_analysis = log_parser.analyze_logs_basic(logs_df)
        
        # Загружаем словарь аномалий
        if anomalies_file:
            logger.info(f"Используем пользовательский словарь: {anomalies_file.filename}")
            anomalies_path = os.path.join(temp_dir, anomalies_file.filename)
            await _save_upload_file(anomalies_file, anomalies_path)
        else:
            # Проверяем, только если это ZIP архив
            if log_file.filename.lower().endswith('.zip'):
                extracted_anomalies = [f for f in log_parser.extract_zip(log_file_path, temp_dir) 
                                      if f.endswith('anomalies_problems.csv')]
                
                if extracted_anomalies:
                    logger.info(f"Найден словарь в ZIP: {extracted_anomalies[0]}")
                    anomalies_path = extracted_anomalies[0]
                else:
                    anomalies_path = None
            else:
                anomalies_path = None
            
            # Если словарь не найден - используем дефолтный
            if not anomalies_path:
                default_anomalies = os.path.join(
                    os.path.dirname(__file__), 
                    '..', 'src', 'bot', 'services', 'anomalies_problems.csv'
                )
                if os.path.exists(default_anomalies):
                    logger.info("Используем дефолтный словарь аномалий")
                    anomalies_path = default_anomalies
                else:
                    raise HTTPException(
                        status_code=400, 
                        detail="Словарь аномалий не найден. Загрузите файл anomalies_problems.csv"
                    )
        
        # Читаем словарь аномалий
        anomalies_df = pd.read_csv(anomalies_path, sep=';', encoding='utf-8')
        logger.info(f"Загружено {len(anomalies_df)} аномалий из словаря")
        
        # ML-анализ (ЛОГИКА КОЛЛЕГИ БЕЗ ИЗМЕНЕНИЙ)
        ml_analyzer.similarity_threshold = threshold_float
        logger.info(f"Запуск ML-анализа с порогом {threshold_float}")
        results_df = ml_analyzer.analyze_logs_with_ml(logs_df, anomalies_df)
        
        logger.info(f"ML-анализ завершен: найдено {len(results_df)} проблем")
        
        # Получаем статистику
        summary = ml_analyzer.get_analysis_summary(results_df)
        
        # Создаем Excel отчет (ТОЧНО ТАК ЖЕ КАК ДЛЯ ЗАЩИТЫ)
        excel_report_path = None
        if not results_df.empty:
            # Добавляем поле 'Сценарий' для совместимости с report_generator
            results_df_with_scenario = results_df.copy()
            results_df_with_scenario['Сценарий'] = 1  # ID сценария по умолчанию
            
            # Конвертируем DataFrame в формат для report_generator (точно как в боте)
            analysis_results = [{
                'results': results_df_with_scenario.to_dict('records')
            }]
            
            excel_report_path = os.path.join(temp_dir, f"analysis_report_{log_file.filename}.xlsx")
            excel_report_path = report_generator.create_excel_report(
                analysis_results, 
                excel_report_path
            )
            # Перемещаем отчет в постоянную директорию скачиваний
            import shutil
            final_excel_path = os.path.join(REPORTS_DIR, os.path.basename(excel_report_path))
            try:
                shutil.copy2(excel_report_path, final_excel_path)
                excel_report_path = final_excel_path
            except Exception:
                # Если копирование не удалось, оставляем временный путь, но логируем
                logger.warning("Не удалось скопировать Excel в reports/, используется временный файл")
            logger.info(f"Excel отчет создан: {excel_report_path}")
        
        # Формируем ответ
        # Для очень больших результатов отключаем тяжелые HTML графы в ответе
        enable_log_vis = not logs_df.empty and len(logs_df) <= 100_000
        enable_anomaly_graph = not results_df.empty and len(results_df) <= 500

        response = {
            "status": "success",
            "analysis": {
                "basic_stats": basic_analysis,
                "ml_results": summary,
                "threshold_used": threshold_float
            },
            "results": results_df.to_dict('records') if not results_df.empty else [],
            "excel_report": f"/api/v1/download/{os.path.basename(excel_report_path)}" if excel_report_path else None,
            "log_visualization": generate_log_visualization(logs_df) if enable_log_vis else None,
            "anomaly_graph": generate_anomaly_graph(results_df, anomalies_df) if enable_anomaly_graph else None
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Ошибка при анализе: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/download/{filename}")
async def download_report(filename: str):
    """
    Скачивает сгенерированный Excel отчет.
    
    **Формат Excel точно такой же, как для защиты на хакатоне.**
    """
    # Ищем файл в директории reports
    file_path = os.path.join(REPORTS_DIR, filename)
    
    if not os.path.exists(file_path):
        # Если не найден в reports, ищем в temp
        file_path = os.path.join(tempfile.gettempdir(), filename)
    
    if not os.path.exists(file_path):
        logger.warning(f"Excel файл не найден: {filename}")
        raise HTTPException(status_code=404, detail=f"Файл {filename} не найден")
    
    logger.info(f"Скачивание Excel отчета: {file_path}")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.get("/api/v1/anomalies/default")
async def get_default_anomalies():
    """Возвращает дефолтный словарь аномалий."""
    default_anomalies = os.path.join(
        os.path.dirname(__file__), 
        '..', 'src', 'bot', 'services', 'anomalies_problems.csv'
    )
    
    if not os.path.exists(default_anomalies):
        raise HTTPException(status_code=404, detail="Дефолтный словарь не найден")
    
    return FileResponse(
        path=default_anomalies,
        filename="anomalies_problems.csv",
        media_type="text/csv"
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Запуск AtomicHack Log Monitor API")
    logger.info("Используется логика анализа коллеги из core/")
    logger.info("Формат Excel отчетов - как для защиты хакатона")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

