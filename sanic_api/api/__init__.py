from sanic import Sanic
from .api import API, handle_exception
from .validators import validators


def init(sanic_app: Sanic):
    sanic_app.on_request(validators)
    sanic_app.error_handler.add(Exception, handle_exception)
