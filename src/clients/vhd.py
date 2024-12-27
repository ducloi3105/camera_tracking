from json import JSONDecodeError
from src.bases.client import Client
from src.bases.error.client import ClientError


class VHDClient(Client):
    def __init__(self, uri):
        self.uri = uri
        super().__init__()

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
            raise ClientError('SetCamFailed: error code: ' + str(response.status_code))
        try:
            return response.json()
        except Exception as e:
            raise ClientError(e.args)
