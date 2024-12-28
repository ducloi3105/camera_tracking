from src.bases.api.routes import RouteLogicHandler
from src.clients.dcerno import DcernoClient
from src.clients.vhd import VHDClient
from src.bases.error.api import BadRequestParams, ServerError
from src.bases.error.client import ClientError
from config import DCERNO_CONFIG, VHD_CONFIG
from pathlib import Path
import os
import json

config_path = os.path.join(Path.home() / 'Documents', 'decerno_vhd_config.json')


class MicrophoneCallLogicHandler(RouteLogicHandler):
    def run(self, uid: str):
        try:
            client = DcernoClient(
                host=DCERNO_CONFIG['host'],
                port=DCERNO_CONFIG['port'],
                timeout=5
            )
            micro = client.get_microphone_status(uid)
            client.socket.close()
        except ClientError as e:
            raise ServerError(message=e.message)

        if not micro:
            raise BadRequestParams(message='microphone not found')

        micros = self.read()
        position = micros.get(uid)
        if not position:
            raise BadRequestParams(message='Microphone not set preset')

        vhd_client = VHDClient(
            uri=VHD_CONFIG['uri'],
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
