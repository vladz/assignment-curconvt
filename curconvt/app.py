import logging
import asyncio

from aiohttp import web

from . import conf
from .rates import RateLoader
from .routes import setup_routes

logger = logging.getLogger(__name__)


async def init_rate_loader(app: 'web.Application'):
    rate_loader = RateLoader(token=conf.OPENEXCHANGERATES_TOKEN)
    task = asyncio.ensure_future(rate_loader.loading_job())
    app['rates'] = rate_loader
    app.setdefault('jobs', []).append(task)


def init(debug: bool = False) -> 'web.Application':
    logger.info('App starting')
    app = web.Application(debug=debug)
    app.on_startup.append(init_rate_loader)
    setup_routes(app)
    return app


def main(debug: bool = False):
    logger.debug(f'env DEBUG={conf.DEBUG}, PORT={conf.PORT}')
    app = init(debug)
    web.run_app(app, port=conf.PORT)
