from typing import Union, List, Set, Tuple, Dict
import logging
import asyncio

import aiohttp
import trafaret as t

from .meta import MetaSingleton

logger = logging.getLogger(__name__)

AGENT_ADDRESS = 'https://openexchangerates.org/api/latest.json'
CURRENCY_CODES = {'CZK', 'EUR', 'PLN', 'USD'}


class InternalServerError(Exception):
    pass


class RateLoader(metaclass=MetaSingleton):
    def __init__(self, token: str = '', agent_address: str = AGENT_ADDRESS,
                 cur_codes: Union[List, Set, Tuple] = CURRENCY_CODES):
        self.address = agent_address
        self.token = token
        if cur_codes:
            if isinstance(cur_codes, (set, list, tuple)):
                self.cur_codes = set(c.upper() for c in cur_codes)
            else:
                raise TypeError(f'check cur_codes: {cur_codes}')
        self.rates = None

    async def prepare_pairs(self, base: str, loaded_rates: Dict[str, float]):
        new_rates = dict()
        new_rates[base + base] = 1
        for rate in loaded_rates:
            new_rates[base + rate] = loaded_rates[rate]
            new_rates[rate + base] = 1 / loaded_rates[rate]
            new_rates[rate + rate] = 1
        for x in loaded_rates:
            for y in loaded_rates:
                if x != y:
                    new_rates[y + x] = new_rates[y + base] * new_rates[base + x]
                    new_rates[x + y] = new_rates[x + base] * new_rates[base + y]
        self.rates = new_rates

    async def load_rates(self, base: str = 'USD'):
        if base not in self.cur_codes:
            raise TypeError(f'Base not in cur_codes: {self.cur_codes}')
        async with aiohttp.ClientSession() as session:
            symbols = self.cur_codes.difference({base})
            params = {'app_id': self.token, 'prettyprint': str(False), 'base': base, 'symbols': ','.join(symbols)}
            async with session.get(self.address, params=params) as resp:
                logger.debug(f'Resp status: {resp.status}')
                if resp.status == 200:
                    response = await resp.json()
                    logger.debug(f'Resp json: {response}')
                    await self.prepare_pairs(base, response['rates'])
                else:
                    error = await resp.text()
                    raise InternalServerError(f'Agent server error: {error}')

    async def loading_job(self, delay: int = 60 * 60 * 24):
        # load currency rates once per day
        while True:
            asyncio.ensure_future(self.load_rates())
            await asyncio.sleep(delay)


def check_currency_name(name):
    return name.upper() if name.upper() in RateLoader().cur_codes else t.DataError('Not exist in currency list')


query_schema = t.Dict({
    t.Key('amount'): t.Float,
    t.Key('from'): t.String(min_length=3, max_length=3) >> check_currency_name,
    t.Key('to'): t.String(min_length=3, max_length=3) >> check_currency_name
})
