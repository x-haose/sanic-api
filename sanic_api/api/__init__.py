from sanic import Sanic
from sanic.exceptions import NotFound

from ..exception import ServerException
from .api import API
from .handle_exception import not_found, other_exception, server_exception
from .validators import validators


def init(sanic_app: Sanic):
    sanic_app.on_request(validators)
    sanic_app.error_handler.add(ServerException, server_exception)
    sanic_app.error_handler.add(Exception, other_exception)
    sanic_app.error_handler.add(NotFound, not_found)
