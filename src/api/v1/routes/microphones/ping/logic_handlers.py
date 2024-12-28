from src.bases.api.routes import RouteLogicHandler
from src.clients.dcerno import DcernoClient
from src.bases.error.api import BadRequestParams
from src.bases.error.client import ClientError
from config import DCERNO_CONFIG


class MicrophonesPingLogicHandler(RouteLogicHandler):
    def run(self):
        ping = False
        try:
            client = DcernoClient(
                host=DCERNO_CONFIG['host'],
                port=DCERNO_CONFIG['port'],
                timeout=2
            )
            if client.socket:
                ping = True

        except Exception as e:
            print(e)
        return dict(success=ping)