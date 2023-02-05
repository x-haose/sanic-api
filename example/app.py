from pydantic.fields import Field
from pydantic.main import BaseModel
from sanic import Blueprint, Request, Sanic, text
from sanic.worker.loader import AppLoader

from sanic_api import init_api
from sanic_api.api import API
from sanic_api.enum import EnumBase, EnumField

app = Sanic(name="test", configure_logging=False)

user_bp = Blueprint("user", url_prefix="/user")
user_bp.ctx.desc = "用户"


class UserTypeEnum(EnumBase):
    ADMIN = EnumField(value="admin", desc="管理员")
    aa = "ddddd"


class UserModel(BaseModel):
    username: str = Field(title="用户名")
    password: str = Field(title="密码", description="密码，经过md5加密的")
    type: UserTypeEnum = Field(title="用户类型", description=UserTypeEnum.to_desc())


class AddUserReqModel(BaseModel):
    """
    添加请求参数
    """

    user: UserModel = Field(title="用户信息")


class AddUserRespModel(BaseModel):
    """
    响应参数
    """

    uid: int = Field(default=None, title="用户ID", description="创建用户的用户ID")


class UserAddApi(API):
    """
    添加用户API
    """

    json_req: AddUserReqModel
    resp: AddUserRespModel
    description = "这是添加用户API接口"
    tags = ["弃用"]


@app.get("/")
def index(r):
    return text("server")


@user_bp.route("/create_user", methods=["POST"])
async def user_add(request: Request, api: UserAddApi):
    api.resp.uid = 1

    return api.json_resp()


def main():
    api_blueprint = Blueprint.group(url_prefix="/api")
    api_blueprint.append(user_bp)
    app.blueprint(api_blueprint)
    init_api(app)
    return app


if __name__ == "__main__":
    loader = AppLoader(factory=main)
    app = loader.load()
    app.prepare(port=5277, debug=True)
    Sanic.serve(app, app_loader=loader)
