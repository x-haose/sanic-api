from sanic import Blueprint, text

t1_2_blueprint = Blueprint("t1_2_blueprint", url_prefix="/t1_2")
t1_2_blueprint.ctx.desc = "测试蓝图1_2"


@t1_2_blueprint.get("/test")
async def hello(request):
    return text("Hello world!")
