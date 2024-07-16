from aiohttp import web as aio_web

from web.views import get_settings, main_page, save_settings

main_routes = [
    aio_web.get("/", main_page),
    aio_web.get("/settings", get_settings, name="settings"),
    aio_web.post("/settings", save_settings),
]
