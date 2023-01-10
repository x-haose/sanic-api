from sanic import Sanic, text
from sanic.log import logger
from sanic_api import init_api

app = Sanic("Sanic-API", configure_logging=False)


@app.get('/')
async def index(request):
    logger.info("Sanic-API Example")
    logger.info("测试i打印")
    return text("Sanic-API Example")


def main():
    init_api(app)
    app.run(access_log=True)


if __name__ == '__main__':
    main()
