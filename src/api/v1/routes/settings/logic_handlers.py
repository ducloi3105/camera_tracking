from src.bases.api.routes import RouteLogicHandler
from pathlib import Path
import os
import json
from config import DECERNO_VHD_SETTING_PATH


class MicrophoneTrackingLogicHandler(RouteLogicHandler):
    def run(self, tracking_enabled: bool, camera_ip: str):
        setting = self.read() or {}
        ips = VHD_CONFIG['ips']
        if camera_ip not in ips:
            raise BadRequestParams(message='camera not found')
        setting[camera_ip] = tracking_enabled
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
        ips = VHD_CONFIG['ips']
        tracking = self.read() or None
        if not tracking:
            tracking = {}
            for ip in ips:
                tracking[ip] = False
        result = {}
        for ip, enable in tracking.items():
            tracking[ip] = enable
        return result

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
