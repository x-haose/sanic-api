from sanic import Sanic

from sanic_api import api, logger, openapi


def init_api(app: Sanic):
    """
    初始化API
    Args:
        app: Sanic的APP

    Returns:

    """
    logger.init(app)
    api.init(app)
    openapi.init(app)
