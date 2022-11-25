from sanic import Sanic
from sanic.server import HttpProtocol
from .api import handle_exception

from .sanic_http import SanicHttp, proc_response
from .openapi import auto_doc
from .validators import validators


def init_api(app: Sanic):
    app.register_listener(auto_doc, 'before_server_start')
    HttpProtocol.HTTP_CLASS = SanicHttp
    app.on_request(validators)
    app.on_response(proc_response)
    app.error_handler.add(Exception, handle_exception)
