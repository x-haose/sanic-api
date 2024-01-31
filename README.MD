![logo](https://images.haose.pro/2022/12/19/logo_17%3A34%3A07_qkt9yi4d7u.png)

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow.svg?logo=python)]()
[![Sanic](https://img.shields.io/badge/framework-Sanic-Server.svg)](http://www.gnu.org/licenses/agpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Sanic-API

让您的sanic服务程序更好的支持API文档、参数校验、日志打印、响应规范等

## 特性

- 无需任何多余改动，全自动生成openapi文档，使用更加方便

- 基于`pydantic`的参数校验器，让接口的请求及响应更符合你的预期

- 使用`loguru`库代替官方`logging`日志库，并对访问日志进行扩展，支持打印接口耗时、接口参数

- 使用`{code: 0, data: null, msg: ""}`样式的接口返回

- 对接口中的异常进行拦截，及自定义错误码

- 接口返回样式可自定义配置

## 截图

## 路线图

- 增加一键生成预设项目cli命令

- 编写详细文档

- API接口增加请求头、URL路径参数收集和校验:

## 安装

使用 pip 安装 sanic-api

```bash
  pip install sanic-api
```

## 使用方法/示例

```python
from sanic import Sanic, text
from sanic_api import init_api

app = Sanic("Sanic-API")


@app.get('/')
async def index(request):
    return text("Sanic-API Example")


def main():
    init_api(app)
    app.run(access_log=True)


if __name__ == '__main__':
    main()

```

## 开发

要部署这个项目，请运行

```bash
  pip install pdm
  pdm sync
```

## 文档

[文档](https://linktodocumentation)
