from sanic import Sanic
from sanic.log import logger

from example.settings import settings
from sanic_api import init_api
from sanic_api.utils import auto_blueprint


async def main_process_start(sanic_app: Sanic):
    """
    主进程启动之前调用
    Args:
        sanic_app: application

    Returns:

    """
    sanic_cfg = settings.sanic.dict(by_alias=True)
    sanic_app.config.update(sanic_cfg)
    logger.info(f"{sanic_app.name} 服务启动")


async def main_process_stop(sanic_app: Sanic):
    """
    主进程停止之后调用
    Args:
        sanic_app: application

    Returns:

    """

    logger.info(f"{sanic_app.name} 服务停止")


async def before_server_start(sanic_app: Sanic):
    """
    worker启动之前调用
    Args:
        sanic_app: application

    Returns:

    """
    logger.debug(f"Worler {sanic_app.m.pid} 启动")


def app_factory():
    """
    app 工厂方法
    Returns:

    """
    app = Sanic(name="test", configure_logging=False)
    app.main_process_start(main_process_start)
    app.main_process_stop(main_process_stop)
    app.before_server_start(before_server_start)

    auto_blueprint(app, "api")
    init_api(app)

    return app
