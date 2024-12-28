from src.bases.api.routes import RouteLogicHandler
from src.clients.dcerno import DcernoClient
from src.clients.vhd import VHDClient
from src.bases.error.api import BadRequestParams
from config import DCERNO_CONFIG, VHD_CONFIG
from pathlib import Path
import os
import json

config_path = os.path.join(Path.home() / 'Documents', 'decerno_vhd_settings.json')
if not os.path.exists(config_path):
    with open(config_path, 'w') as f:
        json.dump({}, f)


class MicrophoneTrackingLogicHandler(RouteLogicHandler):
    def run(self, tracking_enabled: bool):
        setting = self.read() or {}
        setting['tracking_enabled'] = tracking_enabled
        self.write(setting)

        return setting

    @staticmethod
    def read():
        return json.load(open(config_path, 'r'))

    @staticmethod
    def write(data):
        with open(config_path, 'w') as f:
            json.dump(data, f)
