"""Простой тест для проверки API.

Использует логику коллеги через API.
"""

import requests
import os

API_URL = "http://localhost:8000"


def test_health():
    """Проверка работоспособности API."""
    print("🔍 Проверка health endpoint...")
    response = requests.get(f"{API_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API работает: {data['status']}")
        print(f"   ML модель: {data['ml_model']}")
        return True
    else:
        print(f"❌ API не отвечает: {response.status_code}")
        return False


def test_analyze_logs(log_file_path):
    """Тест анализа логов."""
    if not os.path.exists(log_file_path):
        print(f"❌ Файл не найден: {log_file_path}")
        return False
    
    print(f"\n🔍 Анализ файла: {log_file_path}")
    
    with open(log_file_path, 'rb') as f:
        files = {'log_file': f}
        data = {'threshold': 0.7}
        
        response = requests.post(
            f"{API_URL}/api/v1/analyze",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Анализ завершен успешно!")
        print(f"\n📊 Результаты:")
        print(f"   Всего строк: {result['analysis']['basic_stats']['total_lines']}")
        print(f"   Errors: {result['analysis']['basic_stats']['error_count']}")
        print(f"   Warnings: {result['analysis']['basic_stats']['warning_count']}")
        print(f"\n🎯 ML-анализ:")
        print(f"   Найдено проблем: {result['analysis']['ml_results']['total_problems']}")
        print(f"   Уникальных аномалий: {result['analysis']['ml_results']['unique_anomalies']}")
        print(f"   Уникальных проблем: {result['analysis']['ml_results']['unique_problems']}")
        
        if result.get('excel_report'):
            print(f"\n📄 Excel отчет: {API_URL}{result['excel_report']}")
        
        return True
    else:
        print(f"❌ Ошибка анализа: {response.status_code}")
        print(f"   {response.text}")
        return False


def test_download_default_dictionary():
    """Тест скачивания дефолтного словаря."""
    print("\n🔍 Скачивание дефолтного словаря...")
    
    response = requests.get(f"{API_URL}/api/v1/anomalies/default")
    
    if response.status_code == 200:
        print(f"✅ Словарь доступен")
        return True
    else:
        print(f"❌ Словарь недоступен: {response.status_code}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Тестирование AtomicHack Log Monitor API")
    print("=" * 60)
    
    # Проверка health
    if not test_health():
        print("\n⚠️  API не запущен. Запустите: cd api && python main.py")
        exit(1)
    
    # Тест словаря
    test_download_default_dictionary()
    
    # Тест анализа
    # Укажите путь к тестовому файлу логов
    test_file = "Test Cases/TestCase1/Logs.txt"
    
    if os.path.exists(test_file):
        test_analyze_logs(test_file)
    else:
        print(f"\n⚠️  Тестовый файл не найден: {test_file}")
        print("   Укажите путь к файлу логов в test_api.py")
    
    print("\n" + "=" * 60)
    print("✅ Тестирование завершено")
    print("=" * 60)
    print("\n📖 Документация: http://localhost:8000/docs")

