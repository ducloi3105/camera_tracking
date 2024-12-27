import time
from functools import wraps
from requests.exceptions import (
    ConnectionError, ConnectTimeout, SSLError, ChunkedEncodingError
)


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
                    return response
                except (ConnectTimeout,
                        ConnectionError,
                        ChunkedEncodingError,
                        SSLError) as e:
                    error = e
                    retry_count += 1
                    time.sleep(retry_count ** 2)
            raise error

        return handle

    return decorator


def request_server_error_handler(max_retry=2):
    def decorator(func):
        @wraps(func)
        def handle(*args, **kwargs):
            retry_count = 0
            response = func(*args, **kwargs)
            while retry_count < max_retry:
                if response.status_code < 500:
                    break
                response = func(*args, **kwargs)
                retry_count += 1
                time.sleep(retry_count ** 2)
                continue
            return response

        return handle

    return decorator
