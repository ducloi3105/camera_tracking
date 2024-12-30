from src.bases.api.routes import RouteLogicHandler
from src.clients.vhd import VHDClient
from src.bases.error.client import ClientError
from config import VHD_CONFIG


class CameraPingLogicHandler(RouteLogicHandler):
    def run(self):
        pong = False
        try:
            client = VHDClient(
                uri=VHD_CONFIG['uri'],
                logger=self.logger
            )
            res = client.ping()
            pong = True
        except Exception as e:
            pass
        return {
            'success': pong
        }
