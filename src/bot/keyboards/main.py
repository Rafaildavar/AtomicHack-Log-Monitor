"""Клавиатура главного меню бота."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def build_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Создаёт клавиатуру с основными действиями пользователя."""

    # Кнопки меню
    buttons = [
        [KeyboardButton(text="Загрузить логи")],
        [KeyboardButton(text="Справка")],
    ]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

