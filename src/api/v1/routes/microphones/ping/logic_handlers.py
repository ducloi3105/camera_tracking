from src.bases.api.routes import RouteLogicHandler
from src.clients.dcerno import DcernoClient
from src.bases.error.client import ClientError
from config import DCERNO_CONFIG


class MicrophonesPingLogicHandler(RouteLogicHandler):
    def run(self):
        ping = False
        client = DcernoClient(
            host=DCERNO_CONFIG['host'],
            port=DCERNO_CONFIG['port'],
            timeout=2
        )
        try:
            if client.socket_manager.socket:
                ping = True
        except ClientError as e:
            print(e)

        return dict(success=ping)