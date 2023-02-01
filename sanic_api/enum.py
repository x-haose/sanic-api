import json
from dataclasses import dataclass, field
from enum import Enum, auto
from types import DynamicClassAttribute
from typing import Any


@dataclass
class EnumField(object):
    """
    枚举字段类
    """

    value: Any = field(default=auto())
    desc: str = field(default_factory=str)


class EnumBase(Enum):
    """
    枚举基类
    """

    @classmethod
    def _missing_(cls, value: object):
        result = list(filter(lambda d: d.value == value, cls))
        return result[0] if result else None

    @DynamicClassAttribute
    def value(self):
        """
        获取枚举的值
        Returns:

        """
        if isinstance(self._value_, EnumField):
            return self._value_.value
        return self._value_

    @DynamicClassAttribute
    def desc(self):
        """
        获取枚举值的描述
        Returns:

        """
        if isinstance(self._value_, EnumField):
            return self._value_.desc
        else:
            return ""

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def to_desc(cls):
        data = {d.value: d.desc for d in cls}
        return json.dumps(data, ensure_ascii=False)


class RespCodeEnum(EnumBase):
    """
    响应码枚举
    """

    SUCCESS = EnumField(10000, desc="成功")
    FAILED = EnumField(40000, desc="失败")
    PARAM_FAILED = EnumField(40001, desc="参数校验失败")


class ParamEnum(EnumBase):
    """
    参数位置
    """

    JSON = EnumField("json")
    FORM = EnumField("form")
    QUERY = EnumField("query")
