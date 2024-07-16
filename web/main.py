import aiohttp_jinja2
import jinja2
from aiohttp import web as aio_web

from web.routes import main_routes
from web.settings import Settings


def init_func(argv):
    settings = Settings()

    app = aio_web.Application()
    aiohttp_jinja2.setup(app=app, loader=jinja2.FileSystemLoader("web\\templates"))

    app.add_routes(main_routes)
    aio_web.run_app(app, host=settings.host, port=settings.port)
