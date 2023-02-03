from abc import ABCMeta
from dataclasses import dataclass
from functools import partial
from typing import Any, Dict, Optional

# noinspection PyUnresolvedReferences
import ujson
from pydantic import BaseModel
from pydantic import ValidationError as PyDanticValidationError
from sanic import HTTPResponse, Sanic
from sanic.response import json

from sanic_api.enum import ParamEnum, RespCodeEnum
from sanic_api.exception import ValidationError
from sanic_api.model import ListModel
from sanic_api.utils import json_dumps


@dataclass
class Response:
    # http响应码 默认是200
    http_code: int = 200
    # 自定义的响应头
    headers: Optional[Dict[str, str]] = None
    # 自定义的服务码
    server_code: RespCodeEnum = RespCodeEnum.SUCCESS
    # 返回的消息
    message: str = ""
    # 返回的数据
    data: Any = None

    def json_resp(self, dumps=None, **kwargs) -> HTTPResponse:
        """
        返回json格式的响应
        Args:
            dumps: 序列化方法，默认使用自定义的序列化方法
            **kwargs: 序列化方法的参数

        Returns:
            返回一个sanic的HTTPResponse
        """

        if isinstance(self.data, ListModel):
            self.data = self.data.to_list()
        elif isinstance(self.data, BaseModel):
            self.data = self.data.dict()
        else:
            self.data = self.data

        dumps = dumps or partial(ujson.dumps, ensure_ascii=False, default=json_dumps)
        data = {
            self._get_tmp("code_tmp", "code"): self.server_code.value,
            self._get_tmp("msg_tmp", "msg"): self.message or self.server_code.desc,
            self._get_tmp("data_tmp", "data"): self.data,
        }
        return json(
            body=data,
            status=self.http_code,
            headers=self.headers,
            dumps=dumps,
            **kwargs
        )

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
    description: ""

    def __init__(self):
        self.response_type = self.__class__.__annotations__.get("resp")
        self.json_req_type = self.__class__.__annotations__.get("json_req")
        self.form_req_type = self.__class__.__annotations__.get("form_req")
        self.query_req_type = self.__class__.__annotations__.get("query_req")
        try:
            self.resp = (
                self.response_type()
                if self.response_type and issubclass(self.response_type, BaseModel)
                else ""
            )
        except PyDanticValidationError:
            pass

    def req_to_json(self):
        data = {}
        if self.json_req:
            data["json"] = self.json_req.dict()
        elif self.form_req:
            data["form"] = self.form_req.dict()
        if self.query_req:
            data["query"] = self.query_req.dict()

        return ujson.dumps(data, ensure_ascii=False, default=json_dumps, indent=4)

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
            raise ValidationError(e.errors())

    def json_resp(
        self,
        http_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        server_code: RespCodeEnum = RespCodeEnum.SUCCESS,
        message: str = "",
    ):
        """
        根据响应数据返回json格式的响应
        Args:
            http_code: http协议响应码
            headers: 响应头
            server_code: 应用协议响应码
            message: 响应消息

        Returns:
            返回响应
        """

        return Response(
            data=self.resp,
            http_code=http_code,
            headers=headers,
            server_code=server_code,
            message=message,
        ).json_resp()
