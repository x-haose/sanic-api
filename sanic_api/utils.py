import os
from decimal import Decimal
from pathlib import Path
from typing import Optional

import orjson
from sanic import Request
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
