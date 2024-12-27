class Migrator(object):
    def __init__(self, mongodb):
        self.mongodb = mongodb

    def run(self):
        raise NotImplementedError
