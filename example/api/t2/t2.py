from sanic import Blueprint, text

t2_blueprint = Blueprint("t2_blueprint", url_prefix="/t2")
t2_blueprint.ctx.desc = "测试蓝图2"


@t2_blueprint.route("/test", methods=["GET", "POST"])
async def hello(request):
    return text("Hello world!")
