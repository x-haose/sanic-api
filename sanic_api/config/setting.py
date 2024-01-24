from hs_config import ConfigBase
from pydantic import Field

from sanic_api.config.sanic import SanicConfig
from sanic_api.config.sanic_api import SanicApiConfig
from sanic_api.enum import RunModeEnum


class DefaultSettings(ConfigBase):
    """
    配置类
    """

    # 主机
    host: str = Field(default="127.0.0.1")

    # 端口
    port: int = Field(default=5798)

    # 运行模式
    mode: RunModeEnum = Field(default=RunModeEnum.DEV)

    # 工作进程的数量
    workers: int = Field(default=1)

    # sanic 自身的配置
    sanic: SanicConfig = Field(default_factory=SanicConfig)

    # sanic_api 扩展自身需要的配置
    sanic_api: SanicApiConfig = Field(default_factory=SanicApiConfig)
