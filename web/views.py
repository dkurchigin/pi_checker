from datetime import datetime

from aiohttp_jinja2 import template

from web.settings import Settings

settings = Settings()


@template("index.html")
async def main_page(request):
    return {}


@template("settings.html")
async def get_settings(request):
    return {"settings": settings.model_dump()}


@template("settings.html")
async def save_settings(request):
    data = await request.post()

    settings.name = data["name"]
    settings.location = data["location"]
    settings.host = data["host"]
    settings.port = data["port"]
    settings.updated_at = datetime.now()

    settings_map = settings.model_dump()
    with open(".env", encoding="utf-8", mode="w") as env_file:
        for key, value in settings_map.items():
            env_file.write(f'{key.upper()}="{value}"\n')

    return {"settings": settings_map}
