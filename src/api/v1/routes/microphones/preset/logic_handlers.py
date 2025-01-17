from src.bases.api.routes import RouteLogicHandler
from src.clients.dcerno import DcernoClient
from src.clients.vhd import VHDClient
from src.bases.error.api import BadRequestParams
from src.bases.error.client import ClientError
from config import DCERNO_CONFIG, VHD_CONFIG, DECERNO_VHD_MAPPING_PATH
from pathlib import Path
import os
import json


class MicrophonePresetLogicHandler(RouteLogicHandler):
    def run(self, uid: str, camera_ip: str):
        client = DcernoClient(
            host=DCERNO_CONFIG['host'],
            port=DCERNO_CONFIG['port'],
            timeout=5
        )
        try:
            data = client.get_microphone_status(uid)
            if not data:
                raise BadRequestParams(message='microphone not found')
        except ClientError as e:
            raise BadRequestParams(message=e.message)
        ips = VHD_CONFIG['ips']
        if camera_ip not in ips:
            raise BadRequestParams(message='camera not found')
        vhd_client = VHDClient(
            uri=camera_ip,
            logger=self.logger
        )
        micros = self.read()
        if not micros:
            micros = {}
        mapping = {}
        if micros:
            for mic_id, camera_info in micros.items():
                if camera_ip == camera_info['camera_ip']:
                    mapping[mic_id] = camera_info
        if uid in mapping:
            next_number = mapping[uid]['number']
        else:
            next_number = self.find_next_number(mapping)
        micros[uid] = dict(
            camera_ip=camera_ip,
            number=next_number,
            micro_id=uid
        )
        try:
            data = vhd_client.call(
                action='posset',
                position=str(next_number),
            )
        except ClientError as e:
            raise BadRequestParams(message=e.message)
        if not data or data['Response']['Result'] != 'Success':
            raise BadRequestParams(message='Cannot Preset Camera')
        self.write(micros)

        try:
            client.get_all_units()
        except:
            pass
        return dict(success=True)

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

    @staticmethod
    def find_next_number(data):
        if not data:
            return 10
        current_numbers = {int(value) for value in data.values()}

        # Tìm số nhỏ nhất và lớn nhất trong tập hợp
        min_number = min(current_numbers)
        max_number = max(current_numbers)

        # Tìm số bị thiếu đầu tiên trong khoảng
        for number in range(min_number, max_number + 2):
            if number not in current_numbers:
                return number

class MicrophoneDeletePresetLogicHandler(RouteLogicHandler):
    def run(self, uid: str):
        micros = self.read()
        if not micros:
            micros = {}

        micros.pop(uid, None)
        self.write(micros)

        return dict(success=True)

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
