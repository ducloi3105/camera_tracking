import logging

from src.bases.api.generators import ApiGenerator
from src.bases.api.middlewares import LoggingMiddleware

from config import (REDIS, MONGO_URI)

from . import v1


generator = ApiGenerator(
    mongo_config=MONGO_URI,
    router_modules=[v1],
    redis_config=REDIS,
    logger=logging.root,
    middlewares=[LoggingMiddleware],
)

app = generator.run('Storage')
