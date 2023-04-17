from pydantic import BaseModel, Field


class SanicApiConfig(BaseModel):
    """
    sanic_api 框架需要的配置
    """

    data_tmp: str = Field(title="响应中data类型字段的key", default="data")
    code_tmp: str = Field(title="响应中data类型字段的key", default="code")
    msg_tmp: str = Field(title="响应中data类型字段的key", default="msg")
