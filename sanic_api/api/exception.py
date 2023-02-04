from typing import Any, Optional

from sanic.exceptions import SanicException

from sanic_api.enum import EnumBase, RespCodeEnum


class ServerException(SanicException):
    def __init__(
        self,
        message: Optional[str] = None,
        server_code: Optional[EnumBase] = None,
        status_code: Optional[int] = None,
        quiet: Optional[bool] = None,
        context: Any = None,
        extra=None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status_code,
            quiet=quiet,
            context=context,
            extra=extra,
        )
        self.server_code = server_code or RespCodeEnum.FAILED
        self.message = message or self.server_code.desc
        self.status_code = status_code or 200


class ValidationInitError(ServerException):
    """
    验证器初始化失败
    """


class ValidationError(ServerException):
    """
    参数验证失败
    """

    def __init__(self, errors: list, *args, **kwargs):
        super().__init__(server_code=RespCodeEnum.PARAM_FAILED, context=errors)