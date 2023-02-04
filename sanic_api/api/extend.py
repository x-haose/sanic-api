from sanic.exceptions import NotFound
from sanic_ext import Extension

from sanic_api.api.exception import ServerException

from .handle_exception import not_found, other_exception, server_exception
from .validators import validators


class ApiExtend(Extension):
    """
    接口处理扩展
    参数校验、异常拦截等功能
    """

    name = "ApiExtend"

    def startup(self, bootstrap) -> None:
        if not self.included():
            return

        self.app.error_handler.add(ServerException, server_exception)
        self.app.error_handler.add(Exception, other_exception)
        self.app.error_handler.add(NotFound, not_found)
        self.app.on_request(validators, priority=998)
