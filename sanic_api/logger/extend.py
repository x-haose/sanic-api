import logging
import logging.config
import sys
import time

from loguru import logger

# noinspection PyProtectedMember
from loguru._defaults import env
from sanic import HTTPResponse, Request
from sanic.application.constants import Mode
from sanic.server import HttpProtocol
from sanic_ext import Extension

from sanic_api.logger.config import InterceptHandler
from sanic_api.logger.sanic_http import SanicHttp


class LoggerExtend(Extension):
    """
    处理日志的扩展
    """

    name = "LoggerExtend"

    def startup(self, bootstrap) -> None:
        if not self.included():
            return

        log_level = logging.DEBUG if self.app.state.mode is Mode.DEBUG else logging.INFO
        log_format = env(
            "LOGURU_FORMAT",
            str,
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<red>{extra[type]: <10}</red> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - {extra[req_id]}<level>{message}</level>",
        )
        logger.remove()
        logger.add(sys.stdout, colorize=True, format=log_format)

        logging.basicConfig(handlers=[InterceptHandler()], level=log_level, force=True)

        HttpProtocol.HTTP_CLASS = SanicHttp
        self.app.on_request(self.proc_request, priority=999)
        self.app.on_response(self.proc_response, priority=0)

    async def proc_request(self, request: Request):
        """
        处理请求的中间件
        Args:
            request:

        Returns:

        """
        request.ctx.st = time.perf_counter()

    async def proc_response(self, request: Request, response: HTTPResponse):
        """
        处理响应的中间件
        Args:
            request: 请求响应
            response: 响应

        Returns:

        """
        request.ctx.et = time.perf_counter()

        return response
