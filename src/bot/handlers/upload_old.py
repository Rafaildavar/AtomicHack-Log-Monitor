"""Обработчики загрузки и анализа файлов."""

import asyncio
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

logger = logging.getLogger(__name__)

router = Router(name="upload")
file_analyzer = SimpleFileAnalyzer()
log_parser = LogParser()


class UploadStates(StatesGroup):
    """Состояния для процесса загрузки файлов."""
    waiting_for_file = State()


@router.message(F.text == "Загрузить логи")
async def start_upload_process(message: Message, state: FSMContext) -> None:
    """Начинает процесс загрузки файлов логов."""

    await message.answer(
        "📁 Отправьте файл с логами (txt, log или zip архив).\n"
        "Поддерживаются файлы размером до 20MB."
    )
    await state.set_state(UploadStates.waiting_for_file)


@router.message(UploadStates.waiting_for_file, F.document)
async def handle_file_upload(message: Message, state: FSMContext) -> None:
    """Обрабатывает загруженный файл с логами."""

    document = message.document

    # Проверяем размер файла
    if document.file_size and document.file_size > 20 * 1024 * 1024:
        await message.answer(
            "❌ Файл слишком большой (максимум 20MB).\n"
            "Попробуйте сжать файл или отправить меньший."
        )
        return

    # Проверяем расширение файла
    allowed_extensions = ['.txt', '.log', '.zip']
    file_name = document.file_name.lower() if document.file_name else ""

    if not any(file_name.endswith(ext) for ext in allowed_extensions):
        await message.answer(
            "❌ Поддерживаются только файлы .txt, .log или .zip архивы.\n"
            "Пожалуйста, отправьте файл в правильном формате."
        )
        return

    await message.answer("🔄 Анализирую файл... Пожалуйста, подождите.")

    try:
        # ШАГ 1: Скачиваем и распаковываем файл вручную для доступа ко всем файлам
        # ВАЖНО: Не используем process_uploaded_file, так как он очищает временные файлы
        # Сначала скачиваем и распаковываем файл вручную, чтобы получить доступ к файлам
        file_path = await log_parser._download_file(document, message.bot)

        # ШАГ 2: Определяем тип файла и извлекаем содержимое
        if file_path.endswith('.zip'):
            logger.info("Обработка ZIP файла")
            log_files = await log_parser._extract_zip(file_path)
            logger.info(f"Извлечено {len(log_files)} файлов")
        else:
            log_files = [file_path]
            logger.info("Обработка одиночного файла")

        # ШАГ 3: Парсим логи в DataFrame с помощью стандартного парсера
        df = await log_parser._parse_logs_to_dataframe(log_files)
        logs_df = df

        if logs_df.empty:
            await message.answer("❌ В файле не найдено логов в распознаваемом формате.")
            await state.clear()
            return

        # ШАГ 4: Фильтруем только WARNING и ERROR (как в log_to_df.py)
        filtered_logs = anomaly_analyzer.filter_warnings_and_errors(logs_df)

        if filtered_logs.empty:
            await message.answer("❌ В файле не найдено строк с WARNING или ERROR.")
            await state.clear()
            return

        # ШАГ 5: Ищем все словари аномалий в распакованном архиве ДО очистки файлов
        # Это критично - файлы должны быть доступны для поиска anomalies_problems.csv
        anomalies_files = []
        base_dir = None

        if log_files:
            first_file = log_files[0]
            # Используем корневую директорию временных файлов для поиска всех словарей
            base_dir = log_parser.temp_manager.temp_dirs[0] if log_parser.temp_manager.temp_dirs else os.path.dirname(first_file)

        if base_dir:
            # Рекурсивно ищем все файлы anomalies_problems.csv
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file == 'anomalies_problems.csv':
                        anomalies_files.append(os.path.join(root, file))

        logger.info(f"Найдено словарей аномалий: {len(anomalies_files)}")

        if not anomalies_files:
            # Очищаем временные файлы
            log_parser.temp_manager.cleanup()
            await message.answer(
                "⚠️ Словари аномалий не найдены в архиве.\n"
                f"Найдено {len(filtered_logs)} строк с WARNING/ERROR, но сопоставление невозможно."
            )
            await state.clear()
            return

        # ШАГ 6: Обрабатываем каждый сценарий отдельно (как в data_analysis.ipynb)
        # Для каждого словаря аномалий находим соответствующие логи и анализируем
        all_results = []

        for anomalies_file in anomalies_files:
            try:
                # Загружаем словарь аномалий (формат: ID аномалии, Аномалия, ID проблемы, Проблема)
                anomalies_dict = pd.read_csv(anomalies_file, sep=';')
                logger.info(f"Загружен словарь: {anomalies_file} ({len(anomalies_dict)} аномалий)")

                # Определяем папку сценария (например, ValidationCase 1)
                scenario_dir = os.path.dirname(anomalies_file)
                scenario_name = os.path.basename(scenario_dir)

                # Фильтруем логи только из этой папки сценария
                # Ищем файлы, которые находятся в папке с именем сценария
                scenario_logs = filtered_logs[filtered_logs['filename'].apply(
                    lambda x: scenario_name in x and os.path.basename(os.path.dirname(x)) == scenario_name
                )]

                if scenario_logs.empty:
                    logger.warning(f"Для сценария {scenario_name} не найдено логов")
                    continue

                logger.info(f"Анализ сценария {scenario_name}: {len(scenario_logs)} строк логов")

                # ШАГ 7: Находим проблемы для этого сценария (алгоритм из result_df.py)
                # Для каждой строки лога ищем совпадение в столбце "Аномалия"
                # Если нашли - берем соответствующую "Проблему" и ищем её в логах
                scenario_results = anomaly_analyzer.find_anomaly_problem_chain(scenario_logs, anomalies_dict)

                if not scenario_results.empty:
                    # Добавляем информацию о сценарии в результаты
                    scenario_results['Сценарий'] = scenario_name
                    all_results.append(scenario_results)
                    logger.info(f"Найдено {len(scenario_results)} проблем в сценарии {scenario_name}")

            except Exception as e:
                logger.error(f"Ошибка обработки сценария {anomalies_file}: {e}")
                continue

        # Очищаем временные файлы только после полной обработки
        log_parser.temp_manager.cleanup()

        if not all_results:
            await message.answer(
                f"📊 Анализ завершен!\n\n"
                f"Найдено {len(filtered_logs)} строк с WARNING/ERROR,\n"
                f"но известных проблем по словарям не обнаружено."
            )
            await state.clear()
            return

        # ШАГ 8: Объединяем результаты всех сценариев в один DataFrame
        final_results = pd.concat(all_results, ignore_index=True)

        # ШАГ 9: Сохраняем результаты в историю анализа
        # Подготавливаем данные для сохранения в истории
        analysis_data = {
            'total_lines': len(logs_df),
            'error_count': len([row for row in logs_df.itertuples() if row.level.upper() in ['ERROR', 'CRITICAL', 'FATAL']]),
            'warning_count': len([row for row in logs_df.itertuples() if row.level.upper() == 'WARNING']),
            'info_count': len([row for row in logs_df.itertuples() if row.level.upper() == 'INFO']),
            'sources': logs_df['source'].value_counts().to_dict() if 'source' in logs_df.columns else {},
            'top_messages': logs_df['text'].value_counts().head(5).to_dict() if 'text' in logs_df.columns else {},
            'level_distribution': logs_df['level'].value_counts().to_dict() if 'level' in logs_df.columns else {}
        }

        # Сохраняем в историю
        try:
            logger.info(f"Сохраняем анализ в историю: файл={document.file_name}, строк={len(logs_df)}, аномалий={len(final_results) if not final_results.empty else 0}")
            history_service.add_record(
                user_id=message.from_user.id,
                analysis=analysis_data,
                file_name=document.file_name or "unknown_file",
                anomaly_analysis=final_results
            )
            logger.info(f"Результаты анализа сохранены в историю для пользователя {message.from_user.id}")
        except Exception as e:
            logger.error(f"Ошибка сохранения в историю: {e}", exc_info=True)

        # ШАГ 10: Экспортируем в Excel с правильным порядком колонок
        excel_path = anomaly_analyzer.export_to_excel(final_results)

        if not excel_path:
            await message.answer("❌ Ошибка при создании Excel файла.")
            await state.clear()
            return

        # ШАГ 11: Отправляем Excel файл пользователю
        excel_file = FSInputFile(excel_path)

        await message.answer_document(
            excel_file,
            caption=f"📊 Найдено {len(final_results)} проблем в {len(anomalies_files)} сценариях"
        )

        await message.answer(
            f"✅ Анализ завершен!\n\n"
            f"📈 Всего строк проанализировано: {len(logs_df)}\n"
            f"⚠️ Строк с WARNING/ERROR: {len(filtered_logs)}\n"
            f"📋 Сценариев обработано: {len(anomalies_files)}\n"
            f"🚨 Известных проблем найдено: {len(final_results)}\n\n"
            f"Excel файл содержит:\n"
            f"• Сценарий\n"
            f"• ID аномалии\n"
            f"• ID проблемы\n"
            f"• Файл с проблемой\n"
            f"• № строки\n"
            f"• Строка из лога",
            reply_markup=build_main_menu_keyboard()
        )

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
        "❌ Пожалуйста, отправьте файл с логами (txt, log или zip).\n"
        "Используйте кнопку 'Загрузить логи' для начала процесса."
    )

