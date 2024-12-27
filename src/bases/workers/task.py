from celery import Task as _Task


class LogicHandler(object):
    def __init__(self, redis, mongodb):
        self.redis = redis
        self.mongodb = mongodb

    def run(self, *args, **kwargs):
        raise NotImplementedError


class Task(_Task):
    logic_handler_class = LogicHandler

    def run(self, *args, **kwargs):
        logic_handler = self.logic_handler_class(
            redis=self.app.redis,
            mongodb=self.app.mongodb
        )
        logic_handler.run(*args, **kwargs)
