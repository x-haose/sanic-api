import inspect
from collections.abc import Collection
from typing import get_origin

from pydantic import BaseModel
from sanic import Request as SanicRequest
from sanic.compat import Header
from sanic.response import JSONResponse
from sanic_ext.extensions.openapi.builders import OperationStore

from sanic_api.config.setting import JsonRespSettings


class Request(SanicRequest):
    """
    自定义的请求类
    加入便于接口参数获取校验的方法
    """

    json_resp_setting: JsonRespSettings

    json_data: BaseModel
    form_data: BaseModel
    query_data: BaseModel

    _request_type: type["Request"] | None
    _json_data_type: type[BaseModel] | None
    _form_data_type: type[BaseModel] | None
    _query_data_type: type[BaseModel] | None

    def json_resp(
        self,
        data: BaseModel | dict | str | int | float | list,
        server_code: str | int = "",
        server_msg: str = "",
        status: int = 200,
        headers: Header | dict[str, str] | None = None,
    ) -> JSONResponse:
        """
        自定义返回 JSONResponse 的方法
        如果使用了模板模式则返回模板模式的数据
        不使用模版情况下：如果data是dict、list直接返回，否则返回{"data": data}
        Args:
            data: 内容
            server_code: 接口服务码
            server_msg: 接口服务消息
            status: 状态码
            headers: 请求头

        Returns:

        """
        data = data.model_dump(mode="json") if isinstance(data, BaseModel) else data
        if self.json_resp_setting.use_tml:
            data = {
                self.json_resp_setting.code_field_name: server_code,
                self.json_resp_setting.msg_field_name: server_msg,
                self.json_resp_setting.data_field_name: data,
            }
        else:
            data = {"data": data} if type(data) not in (dict, list) else data
        return JSONResponse(data, status=status, headers=headers)

    async def receive_body(self):
        """
        接收请求体
        在这里进行参数校验注入的所有操作
        Returns:

        """
        await super().receive_body()
        self._get_data_type()
        self._load_data()

    def _get_type(self, name: str, base_type: type):
        """
        获取指定属性的类型
        Args:
            name: 属性名字
            base_type: 所属的基本类型

        Returns:
            对于参数返回BaseModel或None
            对于情求类型返回Request或None
        """

        route_handler_arg_spec = inspect.getfullargspec(self.route.handler)
        arg_type = route_handler_arg_spec.annotations.get(name)
        is_name = name in route_handler_arg_spec.args
        is_type = arg_type and issubclass(arg_type, base_type) and arg_type not in (Request, SanicRequest)
        if is_name and is_type:
            return arg_type
        return None

    def _get_data_type(self):
        """
        获取json_data、form_data、query_data、request的类型
        如果定义了request就从request上面获取上述类型
        Returns:

        """

        # 从函数参数注解上面获取类型
        self._json_data_type = self._get_type("json_data", BaseModel)
        self._form_data_type = self._get_type("form_data", BaseModel)
        self._query_data_type = self._get_type("query_data", BaseModel)
        self._request_type = self._get_type("request", Request)

        # 没有json_data参数 但是有自定义的request类就从request类上面获取json_data类型
        if self._request_type and not self._json_data_type:
            self._json_data_type = self._request_type.__annotations__.get("json_data")

        # 没有form_data参数 但是有自定义的request类就从request类上面获取form_data类型
        if self._request_type and not self._form_data_type:
            self._form_data_type = self._request_type.__annotations__.get("form_data")

        # 没有query_data参数 但是有自定义的request类就从request类上面获取query_data类型
        if self._request_type and not self._query_data_type:
            self._query_data_type = self._request_type.__annotations__.get("query_data")

    # noinspection PyBroadException
    def _load_data(self):
        """
        加载json_data、form_data、query_data数据
        同时做参数校验及参数的注入
        Returns:

        """
        route_handler_arg_spec = inspect.getfullargspec(self.route.handler)

        def _set_arg(name, value):
            arg_type = route_handler_arg_spec.annotations.get(name)
            if name in route_handler_arg_spec.args and issubclass(arg_type, BaseModel):
                self.match_info.update({name: value})

        def _proc_param_data(data: dict, data_type: BaseModel | None):
            for k, v in data.items():
                if isinstance(v, list) and len(v) == 1:
                    field = data_type.model_fields.get(k)
                    if not field:
                        continue
                    arg_type = field.annotation
                    arg_type = get_origin(arg_type) or arg_type
                    is_list = issubclass(arg_type, Collection) and arg_type is not str
                    if not is_list:
                        data[k] = v[0]
            return data

        try:
            json_data = self.json
        except Exception:
            json_data = None
        if json_data and self._json_data_type:
            self.json_data = self._json_data_type(**json_data)
            _set_arg("json_data", self.json_data)

        # 由于form和query的参数的key是可以重复的，所以默认类型是类似dict[str, list]的
        # 这里做了个处理，如果key的数量是1个则直接转为dict[str, dict]
        try:
            form_data = self.form
        except Exception:
            form_data = None
        if form_data and self._form_data_type:
            form_data = _proc_param_data(form_data, self._form_data_type)
            self.form_data = self._form_data_type(**form_data)
            _set_arg("form_data", self.form_data)

        try:
            query_data = self.args
        except Exception:
            query_data = None
        if query_data and self._query_data_type:
            query_data = _proc_param_data(query_data, self._query_data_type)
            self.query_data = self._query_data_type(**query_data)
            _set_arg("query_data", self.query_data)

    def _set_openapi(self):
        """
        注入 OpenAPI 信息
        """

        func = self.route.handler

        # 设置接口的概括和描述
        api_doc = self._request_type.__doc__ if self._request_type else func.__doc__

        if api_doc:
            api_doc = api_doc.strip()
            summary = api_doc.split("\n")[0]
            description = "\n".join(api_doc.split("\n")[1:])

            OperationStore()[func].describe(summary=summary, description=description)
