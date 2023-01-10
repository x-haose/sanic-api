from sanic import Sanic
from sanic_ext import Extend

from sanic_api import api, logger, openapi

from .logger import LoggerExtend


def init_api(app: Sanic):
    """
    初始化API
    Args:
        app: Sanic的APP

    Returns:

    """
    Extend.register(logger.LoggerExtend)
    api.init(app)
    openapi.init(app)
