from sanic import Sanic

from sanic_api import api, logger, openapi


def init_api(app: Sanic):
    """
    初始化API
    Args:
        app: Sanic的APP

    Returns:

    """
    api.init(app)
    logger.init(app)
    openapi.init(app)
