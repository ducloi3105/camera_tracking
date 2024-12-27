import requests

from src.common.decorators import (request_connection_handler,
                                   request_server_error_handler)
from src.common.utils import log_data
from src.bases.error.client import ClientError
from src.bases.request_handler import RequestHandler


class Client(RequestHandler):
    pass
