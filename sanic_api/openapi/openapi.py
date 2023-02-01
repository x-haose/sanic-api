import inspect

from pydantic import BaseModel
from sanic import Sanic
from sanic_ext.extensions.openapi.builders import (
    OperationBuilder,
    OperationStore,
    SpecificationBuilder,
)
from sanic_ext.extensions.openapi.definitions import Schema
from sanic_ext.extensions.openapi.types import Array, Object
from sanic_ext.utils.route import clean_route_name, get_all_routes

from sanic_api.api import API
from sanic_api.api.validators import get_handler_param
from sanic_api.model import ListModel


# noinspection PyUnusedLocal
def auto_doc(app: Sanic, loop):
    config = app.config
    specification = SpecificationBuilder()

    for (
        uri,
        route_name,
        route_parameters,
        method_handlers,
        host,
    ) in get_all_routes(app, config.OAS_URL_PREFIX):

        uri = uri if uri == "/" else uri.rstrip("/")

        for method, _handler in method_handlers:

            if (
                (method == "OPTIONS" and app.config.OAS_IGNORE_OPTIONS)
                or (method == "HEAD" and app.config.OAS_IGNORE_HEAD)
                or method == "TRACE"
            ):
                continue

            api_cls = get_handler_param(_handler)
            if not api_cls:
                continue

            api: API = api_cls()

            operation: OperationBuilder = OperationStore()[_handler]
            operation_exclude = getattr(operation, "_exclude")
            operation_default = getattr(operation, "_default")
            operation_autodoc = getattr(operation, "_autodoc")
            operation_allow_autodoc = getattr(operation, "_allow_autodoc")

            if operation_exclude or "openapi" in operation.tags:
                continue

            # 读取蓝图上面的 blueprint.ctx.desc 属性来代替name设置中文tag名
            if len(route_name.split(".")) > 1:
                blueprint = app.blueprints[route_name.split(".")[0]]
                blueprint.ctx.desc = getattr(blueprint.ctx, "desc") or blueprint.name
                operation.tag(blueprint.ctx.desc)

            docstring = inspect.getdoc(_handler)

            if docstring and app.config.OAS_AUTODOC and operation_allow_autodoc:
                operation.autodoc(docstring)

            if api.json_req_type:
                body_type = api.json_req_type
                mine_type = "application/json"
            elif api.form_req_type:
                body_type = api.form_req_type
                mine_type = "application/x-www-form-urlencoded"
            else:
                body_type, mine_type, body_dict = ["", "", {}]
            if body_type:
                body_schema: dict = body_type.schema(
                    ref_template="#/components/schemas/{model}"
                )
                body_dict = {
                    mine_type: Object(body_schema["properties"]),
                }
                for model_name, schema_model in body_schema.get(
                    "definitions", {}
                ).items():
                    specification.add_component("schemas", model_name, schema_model)
                # noinspection PyProtectedMember
                body_dict[mine_type]._fields['required'] = body_schema.get('required', [])
                operation.body(body_dict)

            if api.query_req_type:
                for k, v in api.query_req_type.schema()[
                    "properties"
                ].items():  # type: (str, dict)
                    operation.parameter(k, Schema(**v))

            if api.response_type:
                if issubclass(api.response_type, BaseModel):
                    schema: Schema = Object(
                        api.response_type.schema(
                            ref_template="#/components/schemas/{model}"
                        )["properties"]
                    )
                    if issubclass(api.response_type, ListModel):
                        schema = Array(schema)
                    operation.response(
                        status=200,
                        content={"application/json": schema},
                        description="成功",
                    )
                    specification.add_component(
                        "schemas", api.response_type.__name__, schema
                    )

            operation_default["operationId"] = f"{method.lower()}~{route_name}"
            operation_default["summary"] = clean_route_name(route_name)

            if host:
                if "servers" not in operation_default:
                    operation_default["servers"] = []
                operation_default["servers"].append({"url": f"//{host}"})

            for _parameter in route_parameters:
                if any(
                    (
                        param.fields["name"] == _parameter.name
                        for param in operation.parameters
                    )
                ):
                    continue

                kwargs = {}
                if operation_autodoc and (
                    parameters := operation_autodoc.get("parameters")
                ):
                    description = None
                    for param in parameters:
                        if param["name"] == _parameter.name:
                            description = param.get("description")
                            break
                    if description:
                        kwargs["description"] = description

                operation.parameter(_parameter.name, _parameter.cast, "path", **kwargs)

            operation._app = app
            specification.operation(uri, method, operation)
