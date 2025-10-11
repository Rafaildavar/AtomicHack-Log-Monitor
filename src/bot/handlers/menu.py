"""Обработчики кнопок главного меню."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..handlers.upload import UploadStates
from ..keyboards.main import build_main_menu_keyboard

router = Router(name="menu")


@router.message(F.text == "Загрузить логи")
async def handle_upload_request(message: Message, state: FSMContext) -> None:
    """Начинает процесс загрузки файлов логов."""

    await message.answer(
        "📁 Отправьте файл с логами (txt, log, csv или zip архив).\n"
        "⚠️ Максимальный размер: 20MB (ограничение Telegram Bot API)\n\n"
        "💡 Для больших файлов используйте архивацию с максимальным сжатием."
    )
    await state.set_state(UploadStates.waiting_for_file)


@router.message(F.text == "Справка")
async def handle_help_request(message: Message) -> None:
    """Справочная информация по возможностям бота."""

    await message.answer(
        "🤖 AtomicHack Log Monitor\n\n"
        "Я анализирую файлы логов и создаю Excel отчеты.\n\n"
        "📋 Функции:\n"
        "• Загрузка файлов (txt, log, csv, zip)\n"
        "• Автоматический анализ содержимого\n"
        "• Создание Excel отчетов с результатами\n\n"
        "📏 Ограничения:\n"
        "• Максимальный размер файла: 20MB\n"
        "• Для больших файлов используйте сжатие\n\n"
        "🚀 Просто загрузите файл и получите подробный отчет!",
        reply_markup=build_main_menu_keyboard()
    )