from pydantic import BaseModel, Field
from sanic import Request, Sanic, text
from sanic.log import logger

from sanic_api import init_api
from sanic_api.api import API
from sanic_api.enum import EnumBase, EnumField

app = Sanic("Sanic-API", configure_logging=False)


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


@app.get("/")
async def index(request):
    logger.info("Sanic-API Example")
    return text("Sanic-API Example")


@app.route("/create_user", methods=["POST"])
async def user_add(request: Request, api: UserAddApi):
    return api.json_resp()


def main():
    app.config["sanic_api"] = {"data_tmp": "d", "code_tmp": "c", "msg_tmp": "m"}
    init_api(app)
    app.run(access_log=True)


if __name__ == "__main__":
    main()
