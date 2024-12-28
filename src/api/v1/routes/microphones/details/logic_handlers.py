from src.bases.api.routes import RouteLogicHandler
from src.clients.dcerno import DcernoClient
from config import DCERNO_CONFIG
from src.bases.error.api import ServerError
from src.bases.error.client import ClientError


class MicrophoneDetailsLogicHandler(RouteLogicHandler):
    def run(self, uid: str):
        try:
            client = DcernoClient(
                host=DCERNO_CONFIG['host'],
                port=DCERNO_CONFIG['port'],
                timeout=5
            )
            data = client.get_microphone_status(uid) or {}
            client.socket.close()
        except ClientError as e:
            raise ServerError(message=e.message)

        return data
