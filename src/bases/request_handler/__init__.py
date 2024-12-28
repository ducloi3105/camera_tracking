import logging
import time
import json
import requests
from functools import wraps
from requests.exceptions import ConnectionError, ConnectTimeout

from src.common.json_encoders import CustomJsonEncoder
from src.common.utils import log_data, get_now


def request_connection_handler(max_retry=2):
    def decorator(func):
        @wraps(func)
        def handle(*args, **kwargs):
            retry_count = 0
            error = None
            # retry if connection error happens
            while retry_count < max_retry:
                try:
                    response = func(*args, **kwargs)

                except (ConnectTimeout,
                        ConnectionError) as e:
                    response = None
                    error = e

                if error or (response and response.status_code == 504):
                    retry_count += 1
                    time.sleep(retry_count ** 2)
                    continue

                return response

            raise error

        return handle

    return decorator


class RequestHandler(object):
    trace_id = None

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger

    def _do_request(self, method, url, timeout=10000, **kwargs):
        method_handler = getattr(requests, method, None)
        if not method_handler:
            raise Exception('UnsupportedMethod')

        # handle with ObjectId and Datetime
        json_param = kwargs.get('json')
        if json_param:
            kwargs['json'] = json.loads(
                json.dumps(
                    json_param,
                    cls=CustomJsonEncoder,
                )
            )

        log_data(
            mode='info',
            logger=self.logger,
            kwargs=dict(
                asctime=get_now().isoformat(),
                trace_id=self.trace_id,
                client=self.__class__.__name__,
                method=method,
                url=url,
                payload=kwargs
            )
        )
        response = method_handler(url=url,
                                  timeout=timeout,
                                  **kwargs)
        log_data(
            mode='info',
            logger=self.logger,
            kwargs=dict(
                asctime=get_now().isoformat(),
                trace_id=self.trace_id,
                client=self.__class__.__name__,
                method=method,
                url=url,
                response=response.text
            )
        )
        return response

    def set_trace_id(self, value: str):
        self.trace_id = value
