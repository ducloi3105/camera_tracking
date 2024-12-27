class Job(object):
    def __init__(self, mongodb, logger=None):
        self.mongodb = mongodb
        self.logger = logger

    def run(self, *args, **kwargs):
        raise NotImplementedError
