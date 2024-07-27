import asyncio
from datetime import datetime, timedelta

import aiohttp_jinja2
import jinja2
from aiohttp import web as aio_web

from shatoon.commands import MeasureTemperature, MeasureVoltage, DiskFree
from shatoon.runners import BaseRunner
from web.routes import main_routes
from web.settings import Settings

CHECK_EVERY = timedelta(minutes=1)


async def run_commands():
    previous_run = None
    while True:
        current_dt = datetime.now()
        if previous_run is None or previous_run + CHECK_EVERY < current_dt:
            print(f'{current_dt}: Try to run commands...')
            try:
                await asyncio.gather(
                    BaseRunner.get_result(command_class=MeasureTemperature),
                    BaseRunner.get_result(command_class=MeasureVoltage),
                    BaseRunner.get_result(command_class=DiskFree)
                )
            except Exception as exc:
                print(f'Failed: {str(exc)}')
            current_dt = datetime.now()
            previous_run = current_dt
            print(f'{current_dt}: Done')
            await asyncio.sleep(CHECK_EVERY.seconds)


async def background_tasks(app):
    app['run_commands'] = asyncio.create_task(
        run_commands()
    )
    yield
    app['run_commands'].cancel()
    await app['run_commands']


def init_func(argv):
    settings = Settings()

    app = aio_web.Application()
    aiohttp_jinja2.setup(app=app, loader=jinja2.FileSystemLoader("web\\templates"))

    app.add_routes(main_routes)
    app.cleanup_ctx.append(background_tasks)
    aio_web.run_app(app, host=settings.host, port=settings.port)
