import inspect

from sanic import Request

from sanic_api.api import API
from sanic_api.api.exception import ValidationInitError
from sanic_api.enum import ParamEnum


def _do_validation(param_enum: ParamEnum, api: API, data: dict):
    if param_enum == ParamEnum.JSON:
        req_data = data
    elif param_enum in [ParamEnum.QUERY, param_enum.FORM]:
        req_data = {}
        for k, v in data.items():
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
    # 如果执行中间价直接就发生了异常则直接抛出
    if hasattr(request.ctx, "exception"):
        raise request.ctx.exception

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

    if api.json_req_type and request.json:
        _do_validation(param_enum=ParamEnum.JSON, api=api, data=request.json)
    elif api.form_req_type and request.form:
        _do_validation(param_enum=ParamEnum.FORM, api=api, data=request.form)
    if api.query_req_type and request.query_args:
        _do_validation(param_enum=ParamEnum.QUERY, api=api, data=request.args)

    request.match_info.update({"api": api})
    request.ctx.api = api
