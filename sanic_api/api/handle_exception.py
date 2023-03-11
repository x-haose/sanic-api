from sanic import Request
from sanic.log import logger

from sanic_api.api.api import Response
from sanic_api.api.exception import ServerException
from sanic_api.enum import RespCodeEnum


def server_exception(request: Request, e: ServerException):
    """
    处理业务异常
    Args:
        request: 请求
        e: 异常信息

    Returns:
        返回处理异常后的响应
    """

    return Response(
        http_code=e.status_code,
        server_code=e.server_code,
        message=e.message,
        data=e.context,
    ).json_resp()


def not_found(request: Request, e):
    """
    处理 NotFound 异常
    Args:
        request: 请求信息
        e: 异常信息

    Returns:

    """
    if "/favicon.ico" == request.path:
        return

    logger.warning(f"找不到路由：{request.path}")


def other_exception(request: Request, e):
    """
    处理其他异常
    Args:
        request:
        e:

    Returns:

    """
    logger.exception(e)

    error_name = e.__class__.__name__
    return Response(
        http_code=500,
        server_code=RespCodeEnum.FAILED,
        message=f"服务端业务发生未知异常：[{error_name}] {e}",
    ).json_resp()
