import logging
import logging.config
import sys

from loguru import logger

# noinspection PyProtectedMember
from loguru._defaults import env
from sanic import Sanic
from sanic.server import HttpProtocol

from sanic_api.logger.config import InterceptHandler
from sanic_api.logger.middleware import proc_request, proc_response
from sanic_api.logger.sanic_http import SanicHttp


def init(sanic_app: Sanic):
    """
    初始化日志
    Args:
        sanic_app: Sanic App

    Returns:

    """
    is_debug = sanic_app.config.get("debug")
    log_level = logging.DEBUG if is_debug else logging.INFO
    log_format = env(
        "LOGURU_FORMAT",
        str,
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<red>{extra[type]: <10}</red> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    logger.remove()
    logger.add(sys.stdout, colorize=True, format=log_format)

    logging.basicConfig(handlers=[InterceptHandler()], level=log_level, force=True)

    HttpProtocol.HTTP_CLASS = SanicHttp
    sanic_app.on_request(proc_request)
    sanic_app.on_response(proc_response)
