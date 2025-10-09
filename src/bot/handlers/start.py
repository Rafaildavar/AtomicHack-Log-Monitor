"""Обработчики команд /start и /help."""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from ..keyboards import build_main_menu_keyboard

router = Router(name="start")


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    """Приветствие пользователя и вывод основного меню."""

    await message.answer(
        (
            "Привет! Я бот AtomicHack Log Monitor.\n"
            "Загружай журналы событий и получай анализ аномалий.\n"
            "Выбери действие на клавиатуре ниже."
        ),
        reply_markup=build_main_menu_keyboard(),
    )


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    """Справочная информация по доступным командам."""

    await message.answer(
        (
            "Доступные команды:\n"
            "/start — начать работу и открыть главное меню\n"
            "/help — показать эту подсказку\n"
            "Или воспользуйся кнопками меню для загрузки логов и получения статуса."
        ),
        reply_markup=build_main_menu_keyboard(),
    )

