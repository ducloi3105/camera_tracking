from src.bases.api.routes import RouteLogicHandler
from src.clients.dcerno import DcernoClient
from src.clients.vhd import VHDClient
from src.bases.error.api import BadRequestParams, ServerError
from src.bases.error.client import ClientError
from config import DCERNO_CONFIG, VHD_CONFIG, DECERNO_VHD_MAPPING_PATH
from pathlib import Path
import os
import json


class MicrophoneCallLogicHandler(RouteLogicHandler):
    def run(self, uid: str):
        client = DcernoClient(
            host=DCERNO_CONFIG['host'],
            port=DCERNO_CONFIG['port'],
            timeout=5
        )
        try:
            micro = client.get_microphone_status(uid)
        except ClientError as e:
            raise ServerError(message=e.message)

        if not micro:
            raise BadRequestParams(message='microphone not found')

        micros = self.read()
        micro = micros.get(uid)
        if not micro:
            raise BadRequestParams(message='Microphone not set preset')
        position = micro['number']
        ip = micro['camera_ip']
        vhd_client = VHDClient(
            uri=ip,
            logger=self.logger
        )
        try:
            data = vhd_client.call(
                action='poscall',
                position=str(position),
            )
        except ClientError as e:
            raise ServerError(message=e.message)
        return data

    @staticmethod
    def read():
        if not os.path.exists(DECERNO_VHD_MAPPING_PATH):
            with open(DECERNO_VHD_MAPPING_PATH, 'w') as f:
                json.dump({}, f)
        return json.load(open(DECERNO_VHD_MAPPING_PATH, 'r'))

    @staticmethod
    def write(data):
        with open(DECERNO_VHD_MAPPING_PATH, 'w') as f:
            json.dump(data, f)
