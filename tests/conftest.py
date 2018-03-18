from typing import TYPE_CHECKING, Callable

import pytest

from curconvt import app

if TYPE_CHECKING:
    import asyncio


@pytest.fixture
def cli(loop: 'asyncio.BaseEventLoop', aiohttp_client: Callable) -> 'asyncio.Future.result()':
    test_app = app.init()
    return loop.run_until_complete(aiohttp_client(test_app))
