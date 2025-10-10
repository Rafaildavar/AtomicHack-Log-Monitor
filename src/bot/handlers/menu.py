"""Обработчики кнопок главного меню."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..handlers.upload import UploadStates
from ..services.analysis_history import AnalysisHistory
from ..services.report_generator import ReportGenerator

router = Router(name="menu")
history_service = AnalysisHistory()
report_generator = ReportGenerator()


@router.message(F.text == "Загрузить логи")
async def handle_upload_request(message: Message, state: FSMContext) -> None:
    """Начинает процесс загрузки файлов логов."""

    await message.answer(
        "📁 Отправьте файл с логами (txt, log или zip архив).\n"
        "Поддерживаются файлы размером до 20MB."
    )
    await state.set_state(UploadStates.waiting_for_file)


@router.message(F.text == "Получить статус")
async def handle_status_request(message: Message) -> None:
    """Показывает статистику и историю анализа логов."""

    user_id = message.from_user.id

    # Получаем статистику пользователя
    user_stats = history_service.get_statistics(user_id)
    global_stats = history_service.get_statistics()

    # Получаем последние анализы пользователя
    user_history = history_service.get_user_history(user_id, limit=3)

    text = "📊 Статус системы анализа логов:\n\n"

    # Глобальная статистика
    text += "🌍 Общая статистика:\n"
    text += f"   Анализов: {global_stats['total_analyses']}\n"
    text += f"   Всего ошибок: {global_stats['total_errors']}\n"
    text += f"   Всего предупреждений: {global_stats['total_warnings']}\n"

    if global_stats['avg_errors_per_analysis'] > 0:
        text += f"   Среднее ошибок на анализ: {global_stats['avg_errors_per_analysis']}\n"

    # Статистика пользователя
    text += f"\n👤 Ваша статистика:\n"
    text += f"   Анализов: {user_stats['total_analyses']}\n"
    text += f"   Ваших ошибок: {user_stats['total_errors']}\n"
    text += f"   Ваших предупреждений: {user_stats['total_warnings']}\n"

    # Последние анализы
    if user_history:
        text += "\n📋 Последние анализы:\n"
        for record in user_history:
            text += f"   • {record.file_name} ({record.timestamp[:10]}): "
            text += f"{record.error_count} ошибок, {record.warning_count} предупреждений\n"

    # Топ проблем
    if user_stats['most_common_errors']:
        text += "\n🚨 Ваши топ-проблемы:\n"
        for error, count in list(user_stats['most_common_errors'].items())[:3]:
            text += f"   • {error}: {count} раз\n"

    from ..keyboards.main import build_main_menu_keyboard
    await message.answer(text, reply_markup=build_main_menu_keyboard())


@router.message(F.text == "Экспорт отчета")
async def handle_export_request(message: Message) -> None:
    """Генерирует и отправляет отчет анализа логов."""

    user_id = message.from_user.id
    user_history = history_service.get_user_history(user_id, limit=1)

    if not user_history:
        await message.answer(
            "❌ У вас нет истории анализа логов.\n"
            "Сначала загрузите файл с логами для анализа."
        )
        return

    # Берем последний анализ
    last_analysis = user_history[0]

    await message.answer("📄 Генерирую отчет... Пожалуйста, подождите.")

    try:
        # Генерируем отчеты в разных форматах
        docx_path = await report_generator.generate_docx_report(
            analysis={
                'total_lines': last_analysis.total_lines,
                'error_count': last_analysis.error_count,
                'warning_count': last_analysis.warning_count,
                'sources': last_analysis.sources,
                'top_errors': last_analysis.top_errors
            },
            file_name=last_analysis.file_name,
            user_name=message.from_user.first_name or "Пользователь"
        )

        json_path = await report_generator.generate_json_report(
            analysis={
                'total_lines': last_analysis.total_lines,
                'error_count': last_analysis.error_count,
                'warning_count': last_analysis.warning_count,
                'sources': last_analysis.sources,
                'top_errors': last_analysis.top_errors
            },
            file_name=last_analysis.file_name
        )

        # Отправляем файлы пользователю
        docx_file = await report_generator.get_input_file(docx_path)
        json_file = await report_generator.get_input_file(json_path)

        await message.answer_document(docx_file, caption="📄 Отчет анализа логов (DOCX)")
        await message.answer_document(json_file, caption="📄 Детальные данные анализа (JSON)")

        await message.answer(
            "✅ Отчеты успешно сгенерированы и отправлены!\n"
            "DOCX - форматированный отчет для чтения\n"
            "JSON - структурированные данные для дальнейшего анализа"
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка при генерации отчета: {str(e)}")


@router.message(F.text == "Справка")
async def handle_help_request(message: Message) -> None:
    """Дублируем в кнопке справку по возможностям бота."""

    await message.answer(
        "Я помогу загрузить журналы и обнаружить аномалии."
        "\nКоманды: /start, /help."
        "\nСкоро появятся дополнительные функции анализа в реальном времени.",
    )

