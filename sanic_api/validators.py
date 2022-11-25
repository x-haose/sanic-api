import inspect
import time

from sanic import Request

from .api import API
from .enum import ParamEnum
from .exception import ValidationInitError


def do_validation(param_enum: ParamEnum, api: API, request: Request):
    if param_enum == ParamEnum.JSON:
        req_data = dict(request.json)
    elif param_enum in [ParamEnum.QUERY, param_enum.FORM]:
        req_data = {}
        attr = "args" if param_enum == ParamEnum.QUERY else "form"
        for k, v in getattr(request, attr).items():
            if type(v) == list and len(v) == 1:
                req_data[k] = v[0]
            else:
                req_data[k] = v
    else:
        raise ValidationInitError("未知的验证器类型")

    api.validate_params(req_data, param_enum)


def get_handler_param(handler):
    """
    获取参数处理器的json、form、query参数
    Args:
        handler:

    Returns:

    """
    sig = inspect.signature(handler)
    api_parameter = sig.parameters.get("api")
    api_cls = api_parameter.annotation if api_parameter else None
    return api_cls


async def validators(request: Request):
    """
    校验请求参数中间件
    Args:
        request: 请求

    Returns:

    """
    request.ctx.st = time.perf_counter()
    _, handler, _ = request.app.router.get(
        request.path,
        request.method,
        request.headers.getone("host", None),
    )

    api_cls = get_handler_param(handler)
    if not api_cls:
        return

    api: API = api_cls()
    if api.json_req_type and api.query_req_type:
        raise ValidationInitError("不能同时存在json参数和form参数")

    if api.json_req_type:
        do_validation(param_enum=ParamEnum.JSON, api=api, request=request)
    elif api.form_req_type:
        do_validation(param_enum=ParamEnum.FORM, api=api, request=request)
    if api.query_req_type:
        do_validation(param_enum=ParamEnum.QUERY, api=api, request=request)

    request.match_info.update({"api": api})
    request.ctx.api = api
