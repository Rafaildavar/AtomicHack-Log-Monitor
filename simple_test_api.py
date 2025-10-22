#!/usr/bin/env python3
"""Простой тестовый API без внешних зависимостей для проверки интерфейса."""

import os
import json
from datetime import datetime

# Используем встроенный HTTP сервер Python
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import cgi

class TestAPIHandler(BaseHTTPRequestHandler):
    """Обработчик для тестового API."""

    def do_GET(self):
        """Обработка GET запросов."""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "message": "Тестовый API работает!",
                "status": "ok",
                "endpoints": [
                    "/api/v1/anomalies/default",
                    "/api/v1/analyze (POST)",
                    "/api/v1/download/{filename}"
                ]
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path == '/api/v1/anomalies/default':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = [
                {"id": 1, "pattern": "ERROR", "description": "Ошибки в логах"},
                {"id": 2, "pattern": "WARN", "description": "Предупреждения"},
                {"id": 3, "pattern": "Exception", "description": "Исключения"}
            ]
            self.wfile.write(json.dumps(response).encode())

        elif self.path.startswith('/api/v1/download/'):
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"error": "Файл не найден"}
            self.wfile.write(json.dumps(response).encode())

        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"error": "Эндпоинт не найден"}
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """Обработка POST запросов."""
        if self.path == '/api/v1/analyze':
            try:
                # Получаем размер контента
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)

                # Простой парсинг multipart формы
                content_type = self.headers.get('Content-Type', '')
                if 'multipart/form-data' in content_type:
                    # Извлекаем boundary
                    boundary = content_type.split('boundary=')[1].encode()

                    # Разделяем части
                    parts = post_data.split(b'--' + boundary)

                    file_content = None
                    filename = None
                    threshold = 0.7

                    for part in parts:
                        if b'Content-Disposition: form-data' in part:
                            if b'name="log_file"' in part:
                                # Находим содержимое файла
                                file_start = part.find(b'\r\n\r\n') + 4
                                file_end = part.rfind(b'\r\n')
                                if file_start > 0 and file_end > file_start:
                                    file_content = part[file_start:file_end].decode('utf-8', errors='ignore')
                                    # Извлекаем имя файла из заголовков
                                    if b'filename="' in part:
                                        filename_start = part.find(b'filename="') + 10
                                        filename_end = part.find(b'"', filename_start)
                                        filename = part[filename_start:filename_end].decode()

                            elif b'name="threshold"' in part:
                                # Извлекаем threshold
                                threshold_start = part.find(b'\r\n\r\n') + 4
                                threshold_end = part.rfind(b'\r\n')
                                if threshold_start > 0 and threshold_end > threshold_start:
                                    threshold_str = part[threshold_start:threshold_end].decode()
                                    threshold = float(threshold_str)

                    # Создаем ответ
                    response_data = self.create_analysis_response(file_content, filename, threshold)

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data).encode())

                else:
                    raise ValueError("Не поддерживаемый тип контента")

            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"error": f"Ошибка обработки: {str(e)}"}
                self.wfile.write(json.dumps(response).encode())

        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"error": "Эндпоинт не найден"}
            self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        """Обработка OPTIONS запросов для CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def create_analysis_response(self, content, filename, threshold):
        """Создает ответ анализа."""
        if not content:
            return {"error": "Файл пуст"}

        lines = content.split('\n')
        total_lines = len(lines)
        error_lines = sum(1 for line in lines if 'ERROR' in line.upper())
        warning_lines = sum(1 for line in lines if 'WARN' in line.upper())
        info_lines = total_lines - error_lines - warning_lines

        # Создаем результаты
        results = []
        for i, line in enumerate(lines):  # весь файл
            if any(keyword in line.upper() for keyword in ['ERROR', 'WARN', 'EXCEPTION']):
                results.append({
                    "ID аномалии": len(results) + 1,
                    "ID проблемы": len(results) + 1,
                    "Файл с проблемой": filename or "unknown",
                    "№ строки": i + 1,
                    "Строка из лога": line[:200]
                })

        return {
            "status": "success",
            "message": "Анализ завершен (тестовый режим)",
            "analysis": {
                "basic_stats": {
                    "total_lines": total_lines,
                    "error_count": error_lines,
                    "warning_count": warning_lines,
                    "info_count": info_lines,
                    "sources": {filename or "unknown": total_lines},
                    "level_distribution": {
                        "ERROR": error_lines,
                        "WARN": warning_lines,
                        "INFO": info_lines
                    }
                },
                "ml_results": {
                    "total_problems": len(results),
                    "unique_anomalies": len(results),
                    "unique_problems": len(results),
                    "unique_files": 1
                },
                "threshold_used": threshold
            },
            "results": results,
            "excel_report": "/api/v1/download/test_report.xlsx"
        }

    def log_message(self, format, *args):
        """Логирование запросов."""
        message = format % args
        print(f"[{self.log_date_time_string()}] {message}")

def run_server():
    """Запуск сервера."""
    port = 8001
    server_address = ('', port)
    httpd = HTTPServer(server_address, TestAPIHandler)

    print(f"🚀 Тестовый API запущен на http://localhost:{port}")
    print("📋 Доступные эндпоинты:")
    print("   GET  / - информация о API")
    print("   GET  /api/v1/anomalies/default - словарь аномалий")
    print("   POST /api/v1/analyze - анализ логов")
    print("   GET  /api/v1/download/{filename} - скачивание отчетов")
    print("\n🔄 Нажмите Ctrl+C для остановки")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()
