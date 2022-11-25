from dataclasses import dataclass, field
from enum import Enum, auto
from types import DynamicClassAttribute
from typing import Any


@dataclass
class Field(object):
    """
    枚举字段类
    """
    value: Any = field(default=auto())
    desc: str = field(default_factory=str)


class EnumBase(Enum):
    """
    枚举基类
    """

    @DynamicClassAttribute
    def value(self):
        """
        获取枚举的值
        Returns:

        """
        if isinstance(self._value_, Field):
            return self._value_.value
        return self._value_

    @DynamicClassAttribute
    def desc(self):
        """
        获取枚举值的描述
        Returns:

        """
        if isinstance(self._value_, Field):
            return self._value_.desc
        else:
            return ""

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class RespCodeEnum(EnumBase):
    """
    响应码枚举
    """
    SUCCESS = Field(10000, desc="成功")
    FAILED = Field(40000, desc="失败")

    PARAM_FAILED = Field(40001, desc="参数校验失败")


class ParamEnum(EnumBase):
    """
    参数位置
    """

    JSON = Field('json')
    FORM = Field("form")
    QUERY = Field("query")
