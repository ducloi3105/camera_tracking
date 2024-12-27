import time

from src.bases.api.routes import RouteLogicHandler
from src.clients.vhd import VHDClient
from config import VHD_CONFIG


class CamerasLogicHandler(RouteLogicHandler):
    def run(self):
        client = VHDClient(
            uri=VHD_CONFIG['uri']
        )

        data = client.call(
            action='home',
            position='10',
            zoom='10',
        )
        print(data)
        time.sleep(5)
        data = client.call(
            action='poscall',
            position='2',
        )
        print(data)
        return data