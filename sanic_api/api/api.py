import functools
from abc import ABCMeta
from typing import Any, Callable, Dict, Optional

from pydantic import BaseModel, Field
from pydantic import ValidationError as PyDanticValidationError
from sanic import HTTPResponse, Sanic
from sanic.response import json

from sanic_api.api.exception import ValidationError
from sanic_api.api.model import ListRespModel, ResponseModel
from sanic_api.enum import EnumBase, ParamEnum, RespCodeEnum
from sanic_api.utils import json_dumps


def get_resp_tmp(key: str, default):
    """
    获取响应字段模板
    """
    app = Sanic.get_app()
    sanic_api: dict = app.config.get("sanic_api", {})
    return sanic_api.get(key, default)


class Response:
    def __init__(
        self,
        http_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        server_code: EnumBase = RespCodeEnum.SUCCESS,
        message: str = "Success",
        data: Any = None,
        response_type: Optional[type] = None,
    ):
        """
        初始化函数
        Args:
            http_code: http响应码 默认是200
            headers: 自定义的响应头
            server_code: 自定义的服务码
            message: 返回的消息
            data: 返回的数据
        """

        self.http_code = http_code
        self.headers = headers
        self.message = message
        response_type = response_type or Response.get_response_type(type(data))

        if isinstance(data, ListRespModel):
            data = data.to_list()
        elif isinstance(data, BaseModel):
            data = data.dict()

        resp: ResponseModel = response_type()
        code_tmp = get_resp_tmp("code_tmp", "code")
        msg_tmp = get_resp_tmp("msg_tmp", "msg")
        data_tmp = get_resp_tmp("data_tmp", "data")

        setattr(resp, code_tmp, server_code)
        setattr(resp, msg_tmp, message)
        setattr(resp, data_tmp, data)

        data = resp.dict()

        self.data = data

    def json_resp(self, default: Optional[Callable[[Any], Any]] = None) -> HTTPResponse:
        """
        返回json格式的响应
        Args:

        """
        return json(
            body=self.data,
            status=self.http_code,
            headers=self.headers,
            dumps=functools.partial(json_dumps, default=default),
        )

    @classmethod
    def get_response_type(cls, data_type: type):
        """
        获取响应的类型
        Args:
            data_type: 响应中data的类型

        Returns:

        """
        code_tmp = get_resp_tmp("code_tmp", "code")
        msg_tmp = get_resp_tmp("msg_tmp", "msg")
        data_tmp = get_resp_tmp("data_tmp", "data")

        attr_dict = {
            code_tmp: Field(title="业务响应码"),
            msg_tmp: Field(title="响应消息"),
            data_tmp: Field(title="响应数据"),
            "__annotations__": {code_tmp: int, msg_tmp: str, data_tmp: data_type},
        }
        resp_name = data_type.__name__ if data_type.__name__ != "NoneType" else "Response"
        response_type = type(resp_name, (ResponseModel,), attr_dict)
        return response_type

    @staticmethod
    def _get_tmp(key: str, default):
        """
        获取字段模板
        """
        app = Sanic.get_app()
        sanic_api: dict = app.config.get("sanic_api", {})
        return sanic_api.get(key, default)


class API(metaclass=ABCMeta):
    json_req: Optional[BaseModel] = None
    form_req: Optional[BaseModel] = None
    query_req: Optional[BaseModel] = None
    resp: Optional[Any] = None
    tags: list = []
    description: str = ""

    def __init__(self):
        response_type = self.__class__.__annotations__.get("resp")
        self.json_req_type = self.__class__.__annotations__.get("json_req")
        self.form_req_type = self.__class__.__annotations__.get("form_req")
        self.query_req_type = self.__class__.__annotations__.get("query_req")
        self.response_type = Response.get_response_type(response_type)
        self.resp = response_type()

    def validate_params(self, req_data: dict, param_enum: ParamEnum):
        """
        验证参数，参数有问题抛出异常
        Args:
            req_data: 数据
            param_enum: 参数类型

        Returns:

        """
        try:
            if param_enum == ParamEnum.JSON:
                self.json_req = self.json_req_type(**req_data)
            elif param_enum == ParamEnum.QUERY:
                self.query_req = self.query_req_type(**req_data)
            elif param_enum == ParamEnum.FORM:
                self.form_req = self.form_req_type(**req_data)
        except PyDanticValidationError as e:
            raise ValidationError(e.errors()) from e

    def json_resp(
        self,
        http_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        server_code: RespCodeEnum = RespCodeEnum.SUCCESS,
        message: str = "Success",
    ):
        """
        根据响应数据返回json格式的响应
        Args:
            http_code: http协议响应码
            headers: 响应头
            server_code: 应用协议响应码
            message: 响应消息

        Returns:
            返回一个sanic的HTTPResponse
        """

        return Response(
            data=self.resp,
            http_code=http_code,
            headers=headers,
            server_code=server_code,
            message=message,
            response_type=self.response_type,
        ).json_resp()
