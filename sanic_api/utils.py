import os
import re
from decimal import Decimal
from glob import glob
from importlib import import_module
from inspect import getmembers
from pathlib import Path
from typing import Any, Dict, Optional

import orjson
from sanic import Blueprint, Request, Sanic
from sanic.blueprint_group import BlueprintGroup
from sanic.exceptions import ServerError as SanicServerError


def getpath_by_root(path: str) -> Path:
    """
    根据根目录获取路径
    基于 os.getcwd() 的同级路径、父目录来获取
    Args:
        path: 相对server的子路径

    Returns:
        完整路径
    """
    cwd_path = Path(os.getcwd())
    full_path = Path(os.path.abspath(cwd_path / path))
    return full_path


def json_dumps(data: dict, default=None) -> str:
    """
    调用orjson进行dumps
    Args:
        data: 数据
        default: 数量处理方法

    Returns:
        返回json字符串
    """

    def _default(item):
        if isinstance(item, Decimal):
            return float(item.to_eng_string())

    json_bytes = orjson.dumps(
        data,
        default=default or _default,
        option=orjson.OPT_APPEND_NEWLINE | orjson.OPT_INDENT_2,
    )
    return json_bytes.decode("utf-8")


def get_current_request() -> Optional[Request]:
    """ "
    获取当前请求
    """
    try:
        return Request.get_current()
    except SanicServerError:
        return None


def auto_blueprint(sanic_app: Sanic, base_api_module_name):
    """
    自动生成蓝图
    Args:
        sanic_app: app
        base_api_module_name: api层模块名称

    Returns:

    """
    # app 名称
    app_name = Path(os.getcwd()).parent.name
    # api层名称
    base_api_name: str = base_api_module_name.split(".")[-1]
    # api层模块
    base_api_module = import_module(base_api_module_name, sanic_app.__module__)
    # api层目录
    base_api_dir = Path(str(base_api_module.__file__)).parent

    # 所有路由组的字典
    blueprint_group: Dict[str, BlueprintGroup] = {}

    # 遍历所有__init__文件找到所有蓝图
    for path in glob(f"{base_api_dir}/**/__init__.py", recursive=True):
        # 蓝图所在上层的模块
        modules = re.findall(rf"{app_name}/(.+?)/__", path)[0].split("/")
        specmod = import_module(".".join(modules), sanic_app.__module__)

        # 获取该模块下的所有蓝图
        blueprints = [m[1] for m in getmembers(specmod, lambda o: isinstance(o, Blueprint))]

        blueprint_modules = modules[::-1][1:-1] if modules[-1] != "api" else modules[::-1][:-1]
        for index, m in enumerate(blueprint_modules):
            blueprint_group[m] = blueprint_group.get(m, Blueprint.group(url_prefix=m))
            if index == 0:
                blueprint_group[m].extend(blueprints)
            else:
                prev_bg: Any = blueprint_group.get(blueprint_modules[index - 1])
                blueprint_group[m].append(prev_bg)

    sanic_app.blueprint(blueprint_group[base_api_name])
