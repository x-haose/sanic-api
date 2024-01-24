from decimal import Decimal
from importlib import import_module
from pathlib import Path
from typing import Dict, List, Optional

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
    return (Path.cwd() / path).absolute()


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


def auto_blueprint(sanic_app: Sanic, base_api_module_name: str) -> None:
    """
    自动生成蓝图
    Args:
        sanic_app: app
        base_api_module_name: api层模块名称

    Returns:

    """
    # 导入base_api_module_name模块并获取其文件夹路径
    base_api_dir: Path = Path.cwd() / base_api_module_name

    # 创建根API蓝图组
    root_group: BlueprintGroup = BlueprintGroup(base_api_module_name)

    blueprint_group_map: Dict[str, BlueprintGroup] = {}

    # 遍历所有__init__.py文件，查找蓝图并创建对应的蓝图组
    init_files: List[Path] = list(base_api_dir.glob("**/__init__.py"))
    for file in reversed(init_files):
        # 忽略__init__.py
        init_file: Path = file.parent
        # 获取该蓝图所在的模块路径和名称
        module_path: str = init_file.relative_to(base_api_dir.parent).with_suffix("").as_posix()
        module_name: str = module_path.replace("/", ".")

        # 导入蓝图所在的模块，并获取该模块下的所有蓝图
        module = import_module(module_name, base_api_module_name)
        blueprints = [getattr(module, attr) for attr in dir(module) if isinstance(getattr(module, attr), Blueprint)]
        # 拆分模块路径，创建对应的蓝图组并添加到父级蓝图组中
        parts = [path for path in module_path.split("/") if path not in [base_api_module_name, init_file.name]]

        if len(blueprints) == 1:
            blueprint = blueprints[0]
            if not parts:
                blueprint_group = blueprint_group_map.get(init_file.name)
                if blueprint_group:
                    blueprint.url_prefix = ""
                    blueprint_group.append(blueprint)
                    root_group.append(blueprint_group)
                else:
                    root_group.append(blueprint)
            else:
                for part in parts:
                    group = blueprint_group_map.get(part, BlueprintGroup(part))
                    group.append(blueprint)
                    blueprint_group_map[part] = group
        else:
            group = BlueprintGroup(init_file.name)
            group.extend(blueprints)
            root_group.append(group)

    # 将根API蓝图组添加到应用中
    sanic_app.blueprint(root_group)
