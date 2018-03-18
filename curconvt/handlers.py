from typing import TYPE_CHECKING, Union, Dict
import logging
import json

from aiohttp.web import Response
from trafaret.dataerror import DataError

from .rates import query_schema

if TYPE_CHECKING:
    from aiohttp.web import Request

logger = logging.getLogger(__name__)


def encode(data: Union[tuple, list, dict]) -> bytes:
    return json.dumps(data).encode('utf-8')


async def cur_convert_handler(request: 'Request') -> 'Response':
    data: Dict
    status: int
    body: bytes
    if request.method == 'GET':
        data = request.query
    elif request.method == 'POST':
        data = await request.json()
    logger.debug(f'Request - method: {request.method}, data: {data}')
    try:
        data = await query_schema.async_check(data)
    except DataError as e:
        logging.exception('Wrong request')
        status = 400
        body = encode({'Check params': str(e.error)})
    else:
        status = 200
        rates = request.app['rates'].rates
        pair = data['from'] + data['to']
        rate = rates[pair]
        body = encode({'converted amount': data['amount'] * rate})
    finally:
        logging.debug(f'Response - status: {status}, body: {body}')
        return Response(status=status, body=body, content_type='application/json')
