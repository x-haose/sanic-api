from sanic import Blueprint, Request, text

from sanic_api.api.exception import ServerException

t1_1_blueprint = Blueprint("t1_1_blueprint", url_prefix="/t1_1")
t1_1_blueprint.ctx.desc = "测试蓝图1_1"


@t1_1_blueprint.route("/test", methods=["GET", "POST"])
async def hello(request):
    return text("Hello world!")


@t1_1_blueprint.route("/error", methods=["GET", "POST"])
async def error(request):
    raise ServerException(message="Error")


@t1_1_blueprint.route("/restart", methods=["GET", "POST"])
async def restart(request: Request):
    request.app.m.restart(all_workers=True, zero_downtime=True)
    return text("ok")
