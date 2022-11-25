from pydantic.fields import ModelPrivateAttr
from pydantic.main import BaseModel


class ListModel(BaseModel):
    """
    列表格式的响应模型
    """

    _data_list: list = ModelPrivateAttr(default_factory=list)

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
