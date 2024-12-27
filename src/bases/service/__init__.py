import datetime
import logging

from src.bases.request_handler import RequestHandler
from src.bases.error.service import ServiceError


class Service(RequestHandler):
    base_url = ''

    def __init__(self, access_token: str = None,
                 logger: logging.Logger = None):
        super().__init__(logger=logger)
        self.logger = logger
        self.access_token = access_token

    def do_request(self,
                   method: str,
                   endpoint: str,
                   payload: dict = None,
                   headers: dict = None
                   ):
        request_params = dict(
            method=method.lower(),
            url=self.base_url + endpoint,
        )

        final_headers = {}

        if headers:
            final_headers.update(headers)

        if self.access_token:
            final_headers['Authorization'] = f'Bearer {self.access_token}'

        request_params['headers'] = final_headers

        if payload:
            if method in ['POST', 'PATCH']:
                request_params['json'] = payload
            else:
                params = dict()
                if payload:
                    for k, v in payload.items():
                        params[k] = self._handle_query_param(v)
                request_params['params'] = params

        response = self._do_request(**request_params)

        data = response.json()
        if response.status_code != 200:
            raise ServiceError(data['error'], data['message'])

        return data

    def _handle_query_param(self, value: any) -> str:
        if isinstance(value, list):
            return ','.join(list(map(
                lambda v: self._handle_query_param(v),
                value
            )))

        if isinstance(value, datetime.datetime):
            return value.isoformat()

        if isinstance(value, (float, int, dict)):
            return str(value)

        return value
