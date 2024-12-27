from redis import Redis

from src.bases.databases.mongo import Mongo as BaseMongo


class Mongo(BaseMongo):
    pass


__all__ = (
    'Redis',
    'Mongo'
)
