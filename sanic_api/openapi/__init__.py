from sanic import Sanic

from sanic_api.openapi.openapi import auto_doc


def init(sanic_app: Sanic):
    sanic_app.before_server_start(auto_doc)
