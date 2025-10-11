"""Обработчики загрузки и анализа файлов."""

import logging
import os
import zipfile
from typing import Dict

import pandas as pd
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, Document, FSInputFile

from ..keyboards.main import build_main_menu_keyboard
from ..services.log_parser import LogParser
from ..services.analysis_history import SimpleFileAnalyzer
from ..services.ml_log_analyzer import MLLogAnalyzer

logger = logging.getLogger(__name__)

router = Router(name="upload")
file_analyzer = SimpleFileAnalyzer()
log_parser = LogParser()
ml_analyzer = MLLogAnalyzer()


class UploadStates(StatesGroup):
    """Состояния для процесса загрузки файлов."""
    waiting_for_file = State()


@router.message(F.text == "Загрузить логи")
async def start_upload_process(message: Message, state: FSMContext) -> None:
    """Начинает процесс загрузки файлов логов."""

    await message.answer(
        "📁 Отправьте файл с логами (txt, log, csv или zip архив).\n"
        "Поддерживаются файлы размером до 50MB."
    )
    await state.set_state(UploadStates.waiting_for_file)


@router.message(UploadStates.waiting_for_file, F.document)
async def handle_file_upload(message: Message, state: FSMContext) -> None:
    """Обрабатывает загруженный файл."""

    document = message.document

    # Проверяем размер файла
    if document.file_size and document.file_size > 50 * 1024 * 1024:
        await message.answer(
            "❌ Файл слишком большой (максимум 50MB).\n"
            "Попробуйте сжать файл или отправить меньший."
        )
        return

    await message.answer("🔄 Анализирую файл... Пожалуйста, подождите.")

    try:
        # Скачиваем файл
        file_path = await log_parser._download_file(document, message.bot)

        # ШАГ 1: Определяем сценарии и загружаем словари аномалий
        scenarios_data = {}
        anomalies_files = []

        if file_path.endswith('.zip'):
            # Извлекаем файлы из архива
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(file_path))

            # Находим все файлы anomalies_problems.csv
            extract_dir = os.path.dirname(file_path)
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file == 'anomalies_problems.csv':
                        scenario_name = os.path.basename(os.path.dirname(os.path.join(root, file)))
                        anomalies_files.append((scenario_name, os.path.join(root, file)))
        else:
            # Для одиночного файла проверяем, есть ли словарь в той же папке
            file_dir = os.path.dirname(file_path)
            anomalies_path = os.path.join(file_dir, 'anomalies_problems.csv')
            if os.path.exists(anomalies_path):
                scenario_name = os.path.basename(file_dir)
                anomalies_files.append((scenario_name, anomalies_path))

        logger.info(f"Найдено сценариев: {len(anomalies_files)}")

        if not anomalies_files:
            await message.answer(
                "⚠️ Словари аномалий не найдены.\n"
                "Убедитесь, что в файле есть папки с файлами anomalies_problems.csv."
            )
            await state.clear()
            return

        # ШАГ 2: Обрабатываем каждый сценарий
        all_results = []

        for scenario_name, anomalies_file in anomalies_files:
            try:
                # Загружаем словарь аномалий
                anomalies_dict = pd.read_csv(anomalies_file, sep=';')
                logger.info(f"Загружен словарь для сценария {scenario_name}: {len(anomalies_dict)} аномалий")

                # Находим логи для этого сценария
                scenario_logs = []
                if file_path.endswith('.zip'):
                    # Ищем файлы из той же папки сценария
                    for root, dirs, files in os.walk(os.path.dirname(anomalies_file)):
                        for file in files:
                            if file.endswith('.txt') or file.endswith('.log'):
                                log_path = os.path.join(root, file)
                                try:
                                    with open(log_path, 'r', encoding='utf-8') as f:
                                        lines = f.readlines()

                                    # Парсим строки и фильтруем WARNING/ERROR
                                    for line_num, line in enumerate(lines, 1):
                                        line = line.strip()
                                        if 'WARNING' in line.upper() or 'ERROR' in line.upper():
                                            # Простой парсинг строки
                                            parts = line.split(' ', 2)
                                            if len(parts) >= 3:
                                                dt, level, text = parts[0], parts[1], parts[2]
                                                scenario_logs.append({
                                                    'datetime': dt,
                                                    'level': level,
                                                    'source': 'unknown',
                                                    'text': text,
                                                    'filename': file,
                                                    'line_number': line_num
                                                })
                                except Exception as e:
                                    logger.warning(f"Ошибка чтения файла {log_path}: {e}")
                else:
                    # Одиночный файл
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()

                        for line_num, line in enumerate(lines, 1):
                            line = line.strip()
                            if 'WARNING' in line.upper() or 'ERROR' in line.upper():
                                parts = line.split(' ', 2)
                                if len(parts) >= 3:
                                    dt, level, text = parts[0], parts[1], parts[2]
                                    scenario_logs.append({
                                        'datetime': dt,
                                        'level': level,
                                        'source': 'unknown',
                                        'text': text,
                                        'filename': os.path.basename(file_path),
                                        'line_number': line_num
                                    })
                    except Exception as e:
                        logger.error(f"Ошибка чтения файла {file_path}: {e}")

                if not scenario_logs:
                    logger.warning(f"Для сценария {scenario_name} не найдено WARNING/ERROR строк")
                    continue

                logger.info(f"Анализ сценария {scenario_name}: {len(scenario_logs)} строк логов")

                # ШАГ 3: Используем ML анализатор для поиска аномалий
                logs_df = pd.DataFrame(scenario_logs)
                scenario_results = ml_analyzer.analyze_logs_with_ml(logs_df, anomalies_dict)

                if not scenario_results.empty:
                    # Добавляем информацию о сценарии
                    scenario_results['Сценарий'] = scenario_name
                    all_results.append(scenario_results)
                    logger.info(f"Найдено {len(scenario_results)} проблем в сценарии {scenario_name}")

            except Exception as e:
                logger.error(f"Ошибка обработки сценария {scenario_name}: {e}")
                continue

        # Создаем Excel отчет из результатов анализа
        if all_results:
            final_results = pd.concat(all_results, ignore_index=True)
            excel_path = file_analyzer.create_excel_report([{
                'file_name': document.file_name,
                'analysis_type': 'ml_anomaly_detection',
                'total_scenarios': len(anomalies_files),
                'total_problems': len(final_results),
                'results': final_results.to_dict('records')
            }])
        else:
            excel_path = None

        if excel_path:
            excel_file = FSInputFile(excel_path)
            await message.answer_document(
                excel_file,
                caption=f"📊 ML анализ найденных проблем (Excel) - {len(final_results)} аномалий"
            )

            await message.answer(
                f"✅ ML анализ завершен!\n\n"
                f"📈 Обработано сценариев: {len(anomalies_files)}\n"
                f"🚨 Найдено проблем: {len(final_results)}\n\n"
                f"Excel файл содержит:\n"
                f"• ID аномалии и проблемы\n"
                f"• Файлы и номера строк\n"
                f"• Уверенность ML анализа\n"
                f"• Детали каждой проблемы",
                reply_markup=build_main_menu_keyboard()
            )
        else:
            await message.answer("❌ Ошибка при создании Excel отчета.")

    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {e}", exc_info=True)
        await message.answer(
            f"❌ Произошла ошибка при обработке файла: {str(e)}\n"
            "Попробуйте еще раз или обратитесь к администратору."
        )
    finally:
        # Сбрасываем состояние
        await state.clear()


@router.message(UploadStates.waiting_for_file)
async def handle_invalid_upload(message: Message) -> None:
    """Обрабатывает некорректные сообщения в состоянии ожидания файла."""

    await message.answer(
        "❌ Пожалуйста, отправьте файл с логами (txt, log, csv или zip).\n"
        "Используйте кнопку 'Загрузить логи' для начала процесса."
    )
