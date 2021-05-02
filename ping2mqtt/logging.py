import sys

from loguru import logger

from .settings import general_settings

__all__ = ("logger",)

LoggerFormat = "<green>{time:YY-MM-DD HH:mm:ss.SSS}</green> | " \
               "<level>{level: <8}</level> | " \
               "<level>{message}</level>"

logger.remove()
logger.add(
    sys.stderr,
    level=general_settings.log_level.upper(),
    format=LoggerFormat,
    enqueue=True
)
