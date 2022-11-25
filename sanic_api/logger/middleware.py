import time

from sanic import Request, HTTPResponse


async def proc_request(request: Request, response: HTTPResponse):
    """
    处理请求的中间件
    Args:
        request:
        response:

    Returns:

    """
    request.ctx.st = time.perf_counter()

    return response


async def proc_response(request: Request, response: HTTPResponse):
    """
    处理响应的中间件
    Args:
        request:
        response:

    Returns:

    """
    request.ctx.et = time.perf_counter()

    return response
