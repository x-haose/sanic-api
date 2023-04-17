from pydantic import BaseModel, Field


class SanicConfig(BaseModel):
    """
    sanic 框架本身的配置
    """

    # 是否开启OpenAPI规范文档生成
    oas: bool = Field(default=True)

    # 访问日志开关
    access_log: bool = Field(default=True, alias="ACCESS_LOG", env="ACCESS_LOG")

    # 后台日志记录器，开启可增加一些性能。见：https://sanic.dev/en/plugins/sanic-ext/logger.html
    background_log: bool = Field(default=True, alias="LOGGING", env="LOGGING")

    # OpenAPI规范文档的URL前缀
    oas_url_prefix: str = Field(default="docs", alias="OAS_URL_PREFIX", env="OAS_URL_PREFIX")
