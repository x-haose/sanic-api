from pydantic import BaseModel, Field

from sanic_api.api import API
from sanic_api.api.model import ListRespModel, ResponseModel


class Pagination(BaseModel):
    """
    分页
    """

    page: int = Field(1, gt=0, title="页数")
    per_page: int = Field(20, title="每页数量", gt=0, lt=100)


class ListParam(Pagination):
    """
    列表
    """

    orderings: str = Field(None, title="排序字段", description='排序字段，多个字段 ”,“ 分割，倒序使用 "-", 如："id, -name"')


class UserModel(BaseModel):
    username: str = Field(title="用户名")
    password: str = Field(title="密码", description="密码，经过md5加密的")


class AddUserReqModel(BaseModel):
    """
    添加请求参数
    """

    user: UserModel = Field(title="用户信息")


class AddUserRespModel(ResponseModel):
    """
    响应参数
    """

    uid: int = Field(default=None, title="用户ID", description="创建用户的用户ID")


class FindOneUserRespModel(UserModel, AddUserRespModel):
    """
    响应参数
    """


class UserListRespModel(ListRespModel, FindOneUserRespModel):
    """
    用户列表响应参数
    """


class UserAddApi(API):
    """
    添加用户API
    """

    json_req: AddUserReqModel
    resp: AddUserRespModel


class UserDelApi(API):
    """
    删除用户API
    """

    resp: AddUserRespModel


class UserUpdateApi(UserAddApi):
    """
    更新用户API
    """

    json_req: AddUserReqModel
    resp: AddUserRespModel


class UserFindOneApi(API):
    """
    查询单个用户API
    """

    resp: FindOneUserRespModel


class UserListApi(API):
    """
    用户列表API
    """

    query_req: ListParam
    resp: UserListRespModel
