from pydantic import BaseModel
from sanic import Sanic
from sanic_ext.extensions.openapi.builders import (
    OperationBuilder,
    OperationStore,
    SpecificationBuilder,
)
from sanic_ext.extensions.openapi.definitions import Schema
from sanic_ext.extensions.openapi.types import Array, Object
from sanic_ext.utils.route import get_all_routes

from sanic_api.api import API
from sanic_api.api.model import ListRespModel
from sanic_api.api.validators import get_handler_param


# noinspection PyProtectedMember
def auto_doc(app: Sanic):
    config = app.config
    specification = SpecificationBuilder()

    for (
        uri,
        route_name,
        _route_parameters,
        method_handlers,
        _host,
    ) in get_all_routes(app, config.OAS_URL_PREFIX):
        uri = uri if uri == "/" else uri.rstrip("/")

        for method, _handler in method_handlers:
            if (
                (method == "OPTIONS" and app.config.OAS_IGNORE_OPTIONS)
                or (method == "HEAD" and app.config.OAS_IGNORE_HEAD)
                or method == "TRACE"
            ):
                continue

            if hasattr(_handler, "view_class"):
                _handler = getattr(_handler.view_class, method.lower())
            operation: OperationBuilder = OperationStore()[_handler]

            if operation._exclude or "openapi" in operation.tags:
                continue

            api_cls = get_handler_param(_handler)
            if not api_cls:
                continue

            api: API = api_cls()

            # 读取蓝图上面的 blueprint.ctx.desc 属性来代替name设置中文tag名
            if len(route_name.split(".")) > 1:
                blueprint = app.blueprints[route_name.split(".")[0]]
                blueprint.ctx.desc = blueprint.ctx.desc or blueprint.name
                api.tags.insert(0, blueprint.ctx.desc)

            # 设置接口的标签和描述
            tags = set(api.tags)
            operation.tag(*tags)
            tags_str = " ".join([f"[{tag}](/docs#tag/{tag})" for tag in tags])
            operation.describe(description=f"### 标签: {tags_str}\n{api.description}")

            if api.json_req_type:
                body_type = api.json_req_type
                mine_type = "application/json"
            elif api.form_req_type:
                body_type = api.form_req_type
                mine_type = "application/x-www-form-urlencoded"
            else:
                body_type, mine_type, body_dict = ["", "", {}]

            if body_type:
                body_schema: dict = body_type.schema(ref_template="#/components/schemas/{model}")
                body_dict = {
                    mine_type: Object(body_schema["properties"]),
                }
                for model_name, schema_model in body_schema.get("definitions", {}).items():
                    specification.add_component("schemas", model_name, schema_model)
                body_dict[mine_type]._fields["required"] = body_schema.get("required", [])
                operation.body(body_dict)

            if api.query_req_type:
                for k, v in api.query_req_type.schema()["properties"].items():  # type: (str, dict)
                    operation.parameter(k, Schema(**v))

            if api.response_type and issubclass(api.response_type, BaseModel):
                resp_schema = api.response_type.schema(ref_template="#/components/schemas/{model}")
                schema: Schema = Object(resp_schema["properties"])
                if issubclass(api.response_type, ListRespModel):
                    schema = Array(schema)
                for model_name, schema_model in resp_schema.get("definitions", {}).items():
                    specification.add_component("schemas", model_name, schema_model)
                operation.response(
                    status=200,
                    content={"application/json": schema},
                    description="成功",
                )
                specification.add_component("schemas", api.response_type.__name__, schema)

            operation._app = app
            specification.operation(uri, method, operation)
