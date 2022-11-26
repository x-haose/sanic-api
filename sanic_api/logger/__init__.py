import logging
import logging.config
import sys

from loguru import logger
from sanic import Sanic
from sanic.log import LOGGING_CONFIG_DEFAULTS
from sanic.server import HttpProtocol

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
    log_level = "DEBUG" if is_debug else "INFO"
    logger.configure(handlers=[{"sink": sys.stderr, "level": log_level}])

    sanic_log_config = LOGGING_CONFIG_DEFAULTS
    sanic_log_config["handlers"]["console"]["class"] = "sanic_api.logger.config.InterceptHandler"
    sanic_log_config["handlers"]["error_console"]["class"] = "sanic_api.logger.config.InterceptHandler"
    sanic_log_config["handlers"]["access_console"]["class"] = "sanic_api.logger.config.InterceptHandler"

    if sanic_app.config.get("sql_log"):
        sanic_log_config["loggers"]["tortoise"] = {"level": log_level, "handlers": ["console"]}

    del sanic_log_config["handlers"]["console"]["stream"]
    del sanic_log_config["handlers"]["error_console"]["stream"]
    del sanic_log_config["handlers"]["access_console"]["stream"]

    logging.config.dictConfig(sanic_log_config)

    HttpProtocol.HTTP_CLASS = SanicHttp
    sanic_app.on_request(proc_request)
    sanic_app.on_response(proc_response)
