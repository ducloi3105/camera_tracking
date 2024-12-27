import json


class BaseError(Exception):
    error = None
    message = 'An unknown error happened.'

    def __init__(self, error=None, message=None, meta=None):
        if message:
            self.message = message

        if error:
            self.error = error
        else:
            self.error = self.__class__.__name__

        self.meta = meta

    def output(self):
        data = {
            'message': self.message,
            'error': self.error
        }
        if self.meta:
            data['meta'] = self.meta
        return data

    def __str__(self):
        return json.dumps(self.output())

