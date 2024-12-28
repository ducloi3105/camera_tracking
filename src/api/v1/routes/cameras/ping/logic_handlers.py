from src.bases.api.routes import RouteLogicHandler
from src.clients.vhd import VHDClient
from config import VHD_CONFIG


class CameraPingLogicHandler(RouteLogicHandler):
    def run(self):
        client = VHDClient(
            uri=VHD_CONFIG['uri'],
            logger=self.logger
        )
        pong = False
        res = {}
        try:
            res = client.ping()
            pong = True
        except Exception as e:
            print(e)
        return dict(success=pong, data=str(res))
