from sanic import Sanic
from sanic_ext import Extend

from sanic_api import api, openapi

from .api import ApiExtend
from .logger import LoggerExtend


def init_api(app: Sanic):
    """
    初始化API
    Args:
        app: Sanic的APP

    Returns:

    """
    Extend.register(LoggerExtend)
    Extend.register(ApiExtend)
    openapi.init(app)
