import os
import json
from src.bases.api.routes import RouteLogicHandler
from src.clients.dcerno import DcernoClient
from config import DCERNO_CONFIG, DECERNO_VHD_MAPPING_PATH
from src.bases.error.api import BadRequestParams
from src.bases.error.client import ClientError


class MicrophoneLogicHandler(RouteLogicHandler):
    def run(self):
        client = DcernoClient(
            host=DCERNO_CONFIG['host'],
            port=DCERNO_CONFIG['port']
        )
        try:
            data = client.get_all_units()
        except ClientError as e:
            raise BadRequestParams(message=e.message)
        mics = data['s']
        mapping = self.read()
        for mic in mics:
            mic['preset'] = True if mapping.get(mic['uid']) else False
        return dict(micros=data['s'])

    @staticmethod
    def read():
        if not os.path.exists(DECERNO_VHD_MAPPING_PATH):
            with open(DECERNO_VHD_MAPPING_PATH, 'w') as f:
                json.dump({}, f)
        return json.load(open(DECERNO_VHD_MAPPING_PATH, 'r'))
