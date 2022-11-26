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
