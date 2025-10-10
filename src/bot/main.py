"""Точка входа Telegram-бота."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import settings
from .handlers import menu_router, start_router, upload_router


async def main() -> None:
    """Запуск основного цикла бота в режиме long polling."""

    logging.basicConfig(level=settings.log_level)
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(upload_router)

    # TODO: подключить webhook, если требуется

    logging.info("Запускаем бота в режиме long polling")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Остановка по сигналу KeyboardInterrupt")


