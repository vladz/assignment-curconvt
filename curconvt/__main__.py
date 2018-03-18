import logging
from curconvt import app, conf

try:
    import uvloop
except ImportError:
    pass
else:
    import asyncio

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.DEBUG if conf.DEBUG else logging.INFO)
    app.main(conf.DEBUG)
