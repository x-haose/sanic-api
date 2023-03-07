from sanic import Sanic
from sanic.worker.loader import AppLoader

from example.app import app_factory
from example.settings import settings
from sanic_api.enum import RunModeEnum

if __name__ == "__main__":
    loader = AppLoader(factory=app_factory)
    app = loader.load()
    app.prepare(
        host=settings.host,
        port=settings.port,
        debug=settings.mode == RunModeEnum.DEBUG,
        dev=settings.mode == RunModeEnum.DEV,
        workers=settings.workers,
        fast=settings.mode == RunModeEnum.PRODUCTION and settings.workers == 1,
    )
    Sanic.serve(app, app_loader=loader)
