import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path


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


def json_dumps(item):
    """
    自定义json的dump
    Args:
        item: key

    Returns:

    """
    if isinstance(item, Decimal):
        return float(item.to_eng_string())
    if isinstance(item, datetime):
        return item.isoformat()
