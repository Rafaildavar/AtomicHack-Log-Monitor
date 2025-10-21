"""FastAPI приложение для анализа логов.

Использует те же функции анализа коллеги, что и Telegram бот.
Генерирует Excel отчеты в том же формате, что и для защиты.
"""

import logging
import os
import tempfile
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

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
    threshold: float = 0.7
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
        logger.info(f"Получен запрос на анализ: {log_file.filename}")
        
        # Сохраняем загруженный файл с логами
        log_file_path = os.path.join(temp_dir, log_file.filename)
        with open(log_file_path, 'wb') as f:
            content = await log_file.read()
            f.write(content)
        
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
            with open(anomalies_path, 'wb') as f:
                content = await anomalies_file.read()
                f.write(content)
        else:
            # Проверяем, есть ли в ZIP архиве anomalies_problems.csv
            extracted_anomalies = [f for f in log_parser.extract_zip(log_file_path, temp_dir) 
                                  if f.endswith('anomalies_problems.csv')]
            
            if extracted_anomalies:
                logger.info(f"Найден словарь в ZIP: {extracted_anomalies[0]}")
                anomalies_path = extracted_anomalies[0]
            else:
                # Используем дефолтный словарь
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
        ml_analyzer.similarity_threshold = threshold
        logger.info(f"Запуск ML-анализа с порогом {threshold}")
        results_df = ml_analyzer.analyze_logs_with_ml(logs_df, anomalies_df)
        
        logger.info(f"ML-анализ завершен: найдено {len(results_df)} проблем")
        
        # Получаем статистику
        summary = ml_analyzer.get_analysis_summary(results_df)
        
        # Создаем Excel отчет (ТОЧНО ТАК ЖЕ КАК ДЛЯ ЗАЩИТЫ)
        excel_report_path = None
        if not results_df.empty:
            # Конвертируем DataFrame в формат для report_generator
            analysis_results = [{
                'results': results_df.to_dict('records')
            }]
            
            excel_report_path = os.path.join(temp_dir, f"analysis_report_{log_file.filename}.xlsx")
            excel_report_path = report_generator.create_excel_report(
                analysis_results, 
                excel_report_path
            )
            logger.info(f"Excel отчет создан: {excel_report_path}")
        
        # Формируем ответ
        response = {
            "status": "success",
            "analysis": {
                "basic_stats": basic_analysis,
                "ml_results": summary,
                "threshold_used": threshold
            },
            "results": results_df.to_dict('records') if not results_df.empty else [],
            "excel_report": f"/api/v1/download/{os.path.basename(excel_report_path)}" if excel_report_path else None
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
    # В реальном приложении нужно добавить проверку безопасности и управление временными файлами
    file_path = os.path.join(tempfile.gettempdir(), filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    
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

