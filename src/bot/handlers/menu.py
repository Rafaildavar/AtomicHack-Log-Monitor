"""Обработчики кнопок главного меню."""

from aiogram import F, Router
from aiogram.types import Message

router = Router(name="menu")


@router.message(F.text == "Загрузить логи")
async def handle_upload_request(message: Message) -> None:
    """Заглушка для сценария загрузки логов."""

    await message.answer(
        "Функция загрузки логов пока в разработке."
        "\nСкоро здесь можно будет отправить файлы и получить анализ.",
    )


@router.message(F.text == "Получить статус")
async def handle_status_request(message: Message) -> None:
    """Заглушка для проверки статуса анализа логов."""

    await message.answer(
        "Здесь будет информация о текущем статусе задач анализа."
        "\nПока что нет активных задач.",
    )


@router.message(F.text == "Справка")
async def handle_help_request(message: Message) -> None:
    """Дублируем в кнопке справку по возможностям бота."""

    await message.answer(
        "Я помогу загрузить журналы и обнаружить аномалии."
        "\nКоманды: /start, /help."
        "\nСкоро появятся дополнительные функции анализа в реальном времени.",
    )

