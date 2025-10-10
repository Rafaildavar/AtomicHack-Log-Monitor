"""Обработчики загрузки и анализа файлов логов."""

import asyncio
import logging
from typing import Dict

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, Document

from ..keyboards.main import build_main_menu_keyboard
from ..services.log_parser import LogParser
from ..services.analysis_history import AnalysisHistory

logger = logging.getLogger(__name__)

router = Router(name="upload")
history_service = AnalysisHistory()


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
        # Создаем парсер и анализируем файл
        parser = LogParser()
        result = await parser.process_uploaded_file(document, message.bot)

        if result['success']:
            # Сохраняем запись в историю
            history_service.add_record(
                user_id=message.from_user.id,
                analysis=result['analysis'],
                file_name=document.file_name or "unknown_file"
            )
            await _send_analysis_result(message, result['analysis'])
        else:
            await message.answer(f"❌ Ошибка при анализе файла: {result['error']}")

    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке файла.\n"
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


async def _send_analysis_result(message: Message, analysis: Dict) -> None:
    """Отправляет результаты анализа пользователю."""

    if analysis['total_lines'] == 0:
        await message.answer(
            "📊 Анализ завершен!\n\n"
            "❌ В файле не найдено строк логов в распознаваемом формате.\n"
            "Убедитесь, что файл содержит логи в правильном формате."
        )
        return

    # Формируем сообщение с результатами
    text = "📊 Результаты анализа логов:\n\n"

    text += f"📈 Общее количество строк: {analysis['total_lines']}\n"
    text += f"❌ Ошибок (ERROR/CRITICAL/FATAL): {analysis['error_count']}\n"
    text += f"⚠️ Предупреждений (WARNING): {analysis['warning_count']}\n"
    text += f"ℹ️ Информационных сообщений (INFO): {analysis['info_count']}\n"

    if analysis['time_range']:
        text += f"\n⏰ Временной диапазон:\n"
        text += f"   От: {analysis['time_range']['start']}\n"
        text += f"   До: {analysis['time_range']['end']}\n"

    if analysis['level_distribution']:
        text += "\n📊 Распределение по уровням:\n"
        for level, count in analysis['level_distribution'].items():
            text += f"   • {level}: {count}\n"

    if analysis['sources']:
        text += "\n🔍 Топ источников:\n"
        for source, count in list(analysis['sources'].items())[:5]:
            text += f"   • {source}: {count}\n"

    if analysis['top_messages']:
        text += "\n💬 Наиболее частые сообщения:\n"
        for msg, count in list(analysis['top_messages'].items())[:3]:
            text += f"   • {msg}: {count} раз\n"

    # Добавляем кнопку для возврата в меню
    await message.answer(
        text,
        reply_markup=build_main_menu_keyboard()
    )

    # Если есть много ошибок, предлагаем детальный отчет
    if analysis['error_count'] > 10:
        await message.answer(
            "🔍 Обнаружено много ошибок!\n"
            "Для детального анализа используйте кнопку 'Экспорт отчета'."
        )
