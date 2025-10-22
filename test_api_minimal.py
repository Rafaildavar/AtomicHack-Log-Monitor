#!/usr/bin/env python3
"""Минимальный API для тестирования интерфейса без ML зависимостей."""

import logging
import os
import tempfile
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AtomicHack Log Monitor API (Minimal)",
    description="Минимальный API для тестирования интерфейса",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/analyze")
async def analyze_logs(
    log_file: UploadFile = File(...),
    similarity_threshold: Optional[float] = 0.7
):
    """Анализ логов - минимальная реализация."""
    try:
        logger.info(f"Получен файл: {log_file.filename}")

        # Читаем содержимое файла
        content = await log_file.read()
        content_str = content.decode('utf-8', errors='ignore')

        # Создаем простой анализ
        lines = content_str.split('\n')
        total_lines = len(lines)
        error_lines = sum(1 for line in lines if 'ERROR' in line.upper())
        warning_lines = sum(1 for line in lines if 'WARN' in line.upper())

        # Создаем результат анализа
        analysis_result = {
            "basic_stats": {
                "total_lines": total_lines,
                "error_count": error_lines,
                "warning_count": warning_lines,
                "info_count": total_lines - error_lines - warning_lines
            },
            "ml_results": {
                "anomalies_found": max(0, error_lines - 1),
                "similarity_score": 0.85,
                "confidence": 0.9
            },
            "threshold_used": similarity_threshold
        }

        # Создаем тестовые результаты
        results = []
        for i, line in enumerate(lines[:5]):  # первые 5 строк
            if 'ERROR' in line.upper():
                results.append({
                    "ID аномалии": i + 1,
                    "ID проблемы": i + 1,
                    "Файл с проблемой": log_file.filename or "unknown",
                    "№ строки": i + 1,
                    "Строка из лога": line[:100]
                })

        # Создаем Excel файл
        df = pd.DataFrame(results)
        excel_path = f"/tmp/analysis_{os.path.basename(log_file.filename or 'result')}.xlsx"
        df.to_excel(excel_path, index=False)

        return {
            "status": "success",
            "message": "Анализ завершен (минимальная версия)",
            "analysis": analysis_result,
            "results": results,
            "excel_report": f"/api/v1/download/{os.path.basename(excel_path)}"
        }

    except Exception as e:
        logger.error(f"Ошибка анализа: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/download/{filename}")
async def download_report(filename: str):
    """Скачивание Excel отчета."""
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename
        )
    raise HTTPException(status_code=404, detail="Файл не найден")

@app.get("/api/v1/anomalies/default")
async def get_default_anomalies():
    """Получение словаря аномалий по умолчанию."""
    return [
        {"id": 1, "pattern": "ERROR", "description": "Ошибки в логах"},
        {"id": 2, "pattern": "WARN", "description": "Предупреждения"},
        {"id": 3, "pattern": "Exception", "description": "Исключения"}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
