from src.bases.api.routes import RouteLogicHandler
from src.clients.dcerno import DcernoClient
from src.clients.vhd import VHDClient
from src.bases.error.api import BadRequestParams
from src.bases.error.client import ClientError
from config import DCERNO_CONFIG, VHD_CONFIG
from pathlib import Path
import os
import json

config_path = os.path.join(Path.home() / 'Documents', 'decerno_vhd_camera_config.json')
if not os.path.exists(config_path):
    with open(config_path, 'w') as f:
        json.dump({}, f)


class MicrophonePresetLogicHandler(RouteLogicHandler):
    def run(self, uid: str):
        try:
            client = DcernoClient(
                host=DCERNO_CONFIG['host'],
                port=DCERNO_CONFIG['port'],
                timeout=5
            )
        except Exception as e:
            raise BadRequestParams(message='Could not connect to televic')
        try:
            data = client.get_microphone_status(uid)
            if not data:
                raise BadRequestParams(message='microphone not found')
        except Exception as e:
            raise BadRequestParams(message='microphone not found')

        vhd_client = VHDClient(
            uri=VHD_CONFIG['uri'],
            logger=self.logger
        )
        micros = self.read()
        if micros:
            micros = {}

        if uid in micros:
            next_number = micros[uid]
        else:
            next_number = self.find_next_number(micros)

        micros[uid] = next_number
        try:
            data = vhd_client.call(
                action='posset',
                position=str(next_number),
            )
        except ClientError as e:
            raise BadRequestParams(message='Cannot preset camera')
        if not data or data['Response']['Result'] != 'Success':
            raise BadRequestParams(message='Cannot Preset Camera')

        self.write(micros)

        return dict(success=True)

    @staticmethod
    def read():
        return json.load(open(config_path, 'r'))

    @staticmethod
    def write(data):
        with open(config_path, 'w') as f:
            json.dump(data, f)

    @staticmethod
    def find_next_number(data):
        """
        Tìm giá trị số tiếp theo còn trống trong khoảng từ min đến max.

        Args:
            data (dict): Dictionary chứa các giá trị dạng số dưới dạng string.

        Returns:
            int: Số tiếp theo còn trống.
        """
        # Lấy danh sách các số hiện có và chuyển thành tập hợp số nguyên
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
