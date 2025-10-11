"""Точка входа Telegram-бота."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiohttp import ClientTimeout

from .config import settings
from .handlers import menu_router, start_router, upload_router


async def main() -> None:
    """Запуск основного цикла бота в режиме long polling."""

    logging.basicConfig(level=settings.log_level)
    
    # Создаем сессию с увеличенным таймаутом для загрузки больших файлов
    timeout = ClientTimeout(
        total=300,  # Общий таймаут 5 минут
        connect=60,  # Таймаут подключения 1 минута
        sock_read=180  # Таймаут чтения сокета 3 минуты
    )
    session = AiohttpSession(timeout=timeout)
    
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session
    )
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


