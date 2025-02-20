from json import JSONDecodeError
from src.bases.client import Client
from src.bases.error.client import ClientError


class VHDClient(Client):
    def __init__(self, uri, logger):
        self.uri = f'http://{uri}'
        self.logger = logger

        super().__init__(logger=logger)

    def call(self, action, position=None, zoom=None):
        params = ['ptzcmd', action]

        if position is not None:
            params.append(position)
        if zoom is not None:
            params.append(zoom)
        params = '&'.join(params)
        url = self.uri + f'/cgi-bin/ptzctrl.cgi?{params}'
        try:
            response = self._do_request(
                method='get',
                url=url,
            )
        except Exception as e:
            raise ClientError(e.args)

        if response.status_code != 200:
            raise ClientError(message='SetCamFailed: error code: ' + str(response.status_code))
        try:
            data = response.json()
            if data and data['Response']['Result'] == 'Success':
                return True
        except Exception as e:
            data = response.text
            if isinstance(data, str) and ('success' in data or data == ''):
                return True
        print(f"RESPONSE: {response.text}")
        raise ClientError(message="cannot set preset")

    def ping(self):
        url = self.uri + f'/cgi-bin/param.cgi?get_device_conf'
        try:
            response = self._do_request(
                method='get',
                url=url,
                timeout=3
            )
        except Exception as e:
            raise ClientError(e.args)

        if response.status_code != 200:
            raise ClientError(message='Get device error: error code: ' + str(response.status_code))
        try:
            return response.text
        except Exception as e:
            raise ClientError(e.args)
