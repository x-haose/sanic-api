from sanic import Sanic
from sanic_api.openapi.openapi import auto_doc


def init(sanic_app: Sanic):
    sanic_app.register_listener(auto_doc, 'before_server_start')
