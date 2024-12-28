from src.bases.api.routes import RouteLogicHandler
from src.clients.dcerno import DcernoClient
from config import DCERNO_CONFIG
from src.bases.error.api import BadRequestParams
from src.bases.error.client import ClientError



class MicrophoneLogicHandler(RouteLogicHandler):
    def run(self):
        try:
            client = DcernoClient(
                host=DCERNO_CONFIG['host'],
                port=DCERNO_CONFIG['port']
            )
            data = client.get_all_units()
        except ClientError as e:
            raise BadRequestParams(message=e.message)
        return dict(micros=data['s'])