from src.bases.api.routes import RouteLogicHandler
from pathlib import Path
import os
import json
from config import DECERNO_VHD_SETTING_PATH


class MicrophoneTrackingLogicHandler(RouteLogicHandler):
    def run(self, tracking_enabled: bool):
        setting = self.read() or {}
        setting['tracking_enabled'] = tracking_enabled
        self.write(setting)

        return setting

    @staticmethod
    def read():
        if not os.path.exists(DECERNO_VHD_SETTING_PATH):
            with open(DECERNO_VHD_SETTING_PATH, 'w') as f:
                json.dump({}, f)
        return json.load(open(DECERNO_VHD_SETTING_PATH, 'r'))

    @staticmethod
    def write(data):
        with open(DECERNO_VHD_SETTING_PATH, 'w') as f:
            json.dump(data, f)


class GetMicrophoneTrackingLogicHandler(RouteLogicHandler):
    def run(self):
        return self.read() or {
            'tracking_enabled': False
        }

    @staticmethod
    def read():
        if not os.path.exists(DECERNO_VHD_SETTING_PATH):
            with open(DECERNO_VHD_SETTING_PATH, 'w') as f:
                json.dump({}, f)
        return json.load(open(DECERNO_VHD_SETTING_PATH, 'r'))

    @staticmethod
    def write(data):
        with open(DECERNO_VHD_SETTING_PATH, 'w') as f:
            json.dump(data, f)
