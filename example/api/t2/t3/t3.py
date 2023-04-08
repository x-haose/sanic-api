from sanic import Blueprint, text

t3_blueprint = Blueprint("t3_blueprint", url_prefix="/t3")
t3_blueprint.ctx.desc = "测试蓝图3"


@t3_blueprint.route("/test", methods=["GET", "POST"])
async def hello(request):
    return text("Hello world!")
