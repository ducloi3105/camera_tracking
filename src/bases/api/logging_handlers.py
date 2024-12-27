import json
import logging
from logging import Formatter


class LoggingJsonFormatter(Formatter):
    def format(self, record):
        json_record = {
            'message': record.getMessage(),
        }

        data = getattr(record, 'data', dict())

        for k, v in data.items():
            json_record[k] = v

        if record.levelno == logging.ERROR and record.exc_info:
            json_record['err'] = self.formatException(record.exc_info)

        return json.dumps(json_record)


