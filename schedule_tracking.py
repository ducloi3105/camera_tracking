from pathlib import Path
import os
import json
import time
import logging

from src.clients.dcerno import DcernoClient
from src.clients.vhd import VHDClient
from src.bases.error.client import ClientError
from config import DCERNO_CONFIG, VHD_CONFIG, DECERNO_VHD_SETTING_PATH, DECERNO_VHD_MAPPING_PATH

logger = logging.getLogger()


def run():
    micro_active = None
    vhd_client = VHDClient(uri=VHD_CONFIG['uri'], logger=logger)
    while True:
        time.sleep(1)
        print('====CHECKING camera=====')
        if not os.path.exists(DECERNO_VHD_SETTING_PATH):
            with open(DECERNO_VHD_SETTING_PATH, 'w') as f:
                json.dump({}, f)
        settings = json.load(open(DECERNO_VHD_SETTING_PATH, 'r')) or {}
        if not settings.get('tracking_enabled'):
            continue

        if not os.path.exists(DECERNO_VHD_MAPPING_PATH):
            with open(DECERNO_VHD_MAPPING_PATH, 'w') as f:
                json.dump({}, f)

        dcerno_mapping = json.load(open(DECERNO_VHD_MAPPING_PATH, 'r')) or {}
        if not dcerno_mapping:
            continue

        try:
            client = DcernoClient(
                host=DCERNO_CONFIG['host'],
                port=DCERNO_CONFIG['port']
            )
            data = client.get_all_units()
            client.socket.close()
        except ClientError as e:
            time.sleep(1)
            continue

        active_mic = None
        for micro in data['s']:
            if micro.get('stat') == '1':
                active_mic = micro['uid']
                break
        if not active_mic:
            micro_active = None
            continue
        if active_mic != micro_active:
            micro_active = active_mic

        position = dcerno_mapping.get(micro_active)
        if not position:
            continue
        print(f'set {active_mic} active')
        try:
            vhd_client.call(
                action='poscall',
                position=str(position),
            )
        except ClientError as e:
            time.sleep(1)
            continue


if __name__ == '__main__':
    run()
