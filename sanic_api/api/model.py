from typing import Optional, Union

from pydantic.fields import ModelPrivateAttr
from pydantic.main import BaseModel
from pydantic_core.core_schema import ModelField


class ResponseModel(BaseModel):
    """
    响应基础模型
    """

    def __new__(cls, *args, **kwargs):
        for _field, value in cls.model_fields.items():
            if not isinstance(value, ModelField):
                continue
            value.required = False

        return super().__new__(cls, *args, **kwargs)


class ListRespModel(ResponseModel):
    """
    列表格式的响应基础模型
    """

    _data_list: Optional[Union[ModelPrivateAttr, list]] = ModelPrivateAttr(default_factory=list)

    def add_data(self):
        """
        当前模型下数据添加到列表中
        Returns:

        """
        data = self.dict()
        self._data_list.append(data)
        for attr in data.keys():
            self.__setattr__(attr, None)

    def to_list(self):
        """
        返回列表响应数据
        Returns:

        """
        return self._data_list
