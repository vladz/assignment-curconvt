from os import environ

PORT = environ.get('PORT', 8764)
DEBUG = environ.get('DEBUG', False)
OPENEXCHANGERATES_TOKEN = environ.get('OPENEXCHANGERATES_TOKEN', None)
