from src.bases.api.routes import RouteLogicHandler
from src.clients.dcerno import DcernoClient
from config import DCERNO_CONFIG


class MicrophoneDetailsLogicHandler(RouteLogicHandler):
    def run(self, uid):
        client = DcernoClient(
            host=DCERNO_CONFIG['host'],
            port=DCERNO_CONFIG['port']
        )
        data = client.get_microphone_status(uid)
        return data