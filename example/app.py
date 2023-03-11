import os
import re
from glob import glob
from importlib import import_module
from inspect import getmembers
from pathlib import Path
from typing import Any, Dict

from sanic import Blueprint, Sanic
from sanic.blueprint_group import BlueprintGroup
from sanic.log import logger

from example.settings import settings
from sanic_api import init_api


def init_blueprint(sanic_app: Sanic):
    """
    初始化蓝图
    Returns:

    """
    # app 名称
    app_name = Path(os.getcwd()).parent.name
    # 程序顶层名称
    parent_name: str = os.getcwd().split("/")[-1]
    # api层名称
    base_api_name: str = "api"
    # api层模块名称
    base_api_module_name: str = f"{parent_name}.{base_api_name}"
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


async def main_process_start(sanic_app: Sanic, loop):
    """
    主进程启动之前调用
    Args:
        sanic_app: application
        loop: event loop

    Returns:

    """
    sanic_cfg = settings.sanic.dict(by_alias=True)
    sanic_app.config.update(sanic_cfg)
    logger.info("服务启动")


async def main_process_stop(sanic_app: Sanic, loop):
    """
    主进程停止之后调用
    Args:
        sanic_app: application
        loop: event loop

    Returns:

    """

    logger.info("服务停止")


async def before_server_start(sanic_app: Sanic, loop):
    """
    worker启动之前调用
    Args:
        sanic_app: application
        loop: event loop

    Returns:

    """
    logger.debug(f"Worler {sanic_app.m.pid} 启动")


def app_factory():
    """
    app 工厂方法
    Returns:

    """
    app = Sanic(name="test", configure_logging=False)
    app.main_process_start(main_process_start)
    app.main_process_stop(main_process_stop)
    app.before_server_start(before_server_start)

    init_blueprint(app)
    init_api(app)

    return app
