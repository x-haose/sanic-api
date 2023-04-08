from typing import Any, Dict, List
from uuid import uuid4

from sanic import Blueprint, text
from sanic.request import Request

from .validator import (
    UserAddApi,
    UserDelApi,
    UserFindOneApi,
    UserListApi,
    UserUpdateApi,
)

users_blueprint = Blueprint("users_blueprint", url_prefix="/users")
users_blueprint.ctx.desc = "用户"


@users_blueprint.route("/test", methods=["GET"])
async def hello(request):
    return text("Hello world!")


@users_blueprint.route("/", methods=["POST"])
async def user_add(request: Request, api: UserAddApi):
    """
    添加用户
    """
    api.resp.uid = 1
    return api.json_resp()


@users_blueprint.route("/<uid>", methods=["DELETE"])
async def user_del(request: Request, uid: int, api: UserDelApi):
    """
    刪除一个用户
    """

    api.resp.uid = uid

    return api.json_resp()


@users_blueprint.route("/<uid>", methods=["PUT"])
async def user_update(request: Request, uid: int, api: UserUpdateApi):
    """
    更新一个用户
    """

    api.resp.uid = uid

    return api.json_resp()


@users_blueprint.route("/<uid>", methods=["GET"])
async def user_one(request: Request, uid: int, api: UserFindOneApi):
    """
    获取一个用户
    """

    api.resp.uid = 1
    api.resp.username = "username"
    api.resp.password = uuid4().hex

    return api.json_resp()


@users_blueprint.route("/", methods=["GET"])
async def user_list(request: Request, api: UserListApi):
    """
    获取一些用户
    """

    users: List[Dict[str, Any]] = [
        {
            "uid": 1,
            "username": "user1",
        },
        {
            "uid": 2,
            "username": "user2",
        },
    ]
    for user in users:
        api.resp.username = user["username"]
        api.resp.uid = user["uid"]
        api.resp.add_data()

    return api.json_resp()
