"""Пакет с хэндлерами бота."""

from .start import router as start_router
from .menu import router as menu_router
from .upload import router as upload_router

__all__ = ["start_router", "menu_router", "upload_router"]
