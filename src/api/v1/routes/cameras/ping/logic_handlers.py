from src.bases.api.routes import RouteLogicHandler
from src.clients.vhd import VHDClient
from config import VHD_CONFIG


class CameraPingLogicHandler(RouteLogicHandler):
    def run(self):
        client = VHDClient(
            uri=VHD_CONFIG['uri'],
            logger=self.logger
        )
        res = client.ping()
        return res
