from typing import TYPE_CHECKING
import logging

from .handlers import cur_convert_handler

if TYPE_CHECKING:
    from aiohttp import web

logger = logging.getLogger(__name__)


def setup_routes(app: 'web.Application'):
    logger.info('Init routes')
    app.router.add_get('/', cur_convert_handler)
    app.router.add_post('/', cur_convert_handler)
