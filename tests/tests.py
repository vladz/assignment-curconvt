import pytest
from typing import TYPE_CHECKING
import asyncio
import json

from trafaret import DataError
from aiohttp.client_exceptions import InvalidURL

from curconvt.conf import OPENEXCHANGERATES_TOKEN
from curconvt.handlers import encode
from curconvt.rates import check_currency_name, query_schema, RateLoader, AGENT_ADDRESS, InternalServerError
from curconvt.meta import MetaSingleton

if TYPE_CHECKING:
    from aiohttp.pytest_plugin import TestClient


async def test_rate_loader():
    rl = RateLoader(OPENEXCHANGERATES_TOKEN)
    assert rl.address == AGENT_ADDRESS
    assert rl.token
    assert not rl.rates
    t = asyncio.ensure_future(rl.loading_job())
    while not rl.rates:
        await asyncio.sleep(1)
    t.cancel()
    assert rl.rates

    cur_codes = {'CZK', 'EUR', 'PLN', 'USD'}
    expected = {cur1 + cur2: 1 for cur1 in cur_codes for cur2 in cur_codes}
    await rl.prepare_pairs(base='USD', loaded_rates={'CZK': 1, 'EUR': 1, 'PLN': 1})
    assert rl.rates == expected

    with pytest.raises(TypeError):
        await rl.load_rates(base='QWE')
    with pytest.raises(InternalServerError):
        await rl.load_rates(base='CZK')
    with pytest.raises(InvalidURL):
        rl.address = '123'
        await rl.load_rates()


def test_check_currency_name():
    assert check_currency_name('usd') == 'USD'
    assert isinstance(check_currency_name('usdasd'), DataError)


def test_trafaret_schema():
    expected = {'amount': 111., 'from': 'USD', 'to': 'CZK'}
    assert query_schema.check({'amount': 111, 'from': 'usd', 'to': 'Czk'}) == expected
    with pytest.raises(DataError):
        query_schema.check({'amount': 'aaa', 'from': 'USD', 'to': 'CZK'})
    with pytest.raises(DataError):
        query_schema.check({'amount': 123, 'from': 'zzz', 'to': 'yyy'})


def test_encode():
    test_data = {'amount': 1, 'from': 'USD', 'to': 'CZK'}
    expected = b'{"amount": 1, "from": "USD", "to": "CZK"}'
    assert encode(test_data) == expected


def test_meta():
    class Test(metaclass=MetaSingleton):
        def __init__(self):
            pass

    m1 = Test()
    m2 = Test()
    assert m1 == m2


async def test_handlers(cli: 'TestClient'):
    sended = json.dumps({'amount': '1', 'from': 'usd', 'to': 'usd'})
    fault = json.dumps({'am': '1'})
    expected = {'converted amount': 1.0}

    # Wait rate loading
    while not cli.server.app['rates'].rates:
        await asyncio.sleep(1)
    # Cancel job list
    for task in cli.server.app['jobs']:
        task.cancel()
    # POST
    resp = await cli.post('/', data=sended)
    assert resp.status == 200
    assert await resp.json() == expected
    resp = await cli.post('/', data=fault)
    assert resp.status == 400
    # GET
    resp = await cli.get('/?from=USD&to=USD&amount=1')
    assert resp.status == 200
    assert await resp.json() == expected
    resp = await cli.get('/?from=US&amount=qwe1')
    assert resp.status == 400
    # Other endpoints
    resp = await cli.get('/qwerty')
    assert resp.status == 404
