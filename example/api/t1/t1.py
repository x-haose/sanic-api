from sanic import Blueprint, text

t1_blueprint = Blueprint("t1_blueprint", url_prefix="/t1")
t1_blueprint.ctx.desc = "测试蓝图2"


@t1_blueprint.route("/test", methods=["GET", "POST"])
async def hello(request):
    return text("Hello world!")
