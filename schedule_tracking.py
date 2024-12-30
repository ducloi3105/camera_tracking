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
    vhd_client = VHDClient(uri=VHD_CONFIG['uri'], logger=logger)

    client = DcernoClient(
        host=DCERNO_CONFIG['host'],
        port=DCERNO_CONFIG['port'],
        timeout=5
    )
    try:
        current_active_micro = 'home'

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

            data = client.get_all_units()

            active_micros = []
            for micro in data['s']:
                if micro.get('stat') == '1':
                    active_micros.append(micro['uid'])
            if not active_micros:
                if current_active_micro != 'home':
                    vhd_client.call(
                        action='home',
                        position='10',
                        zoom='10',
                    )
                    current_active_micro = 'home'
                continue

            if current_active_micro in active_micros:
                continue
            else:
                current_active_micro = active_micros[0]

            position = dcerno_mapping.get(current_active_micro)
            if not position:
                continue
            print(f'set {current_active_micro} active')
            vhd_client.call(
                action='poscall',
                position=str(position),
            )
    except Exception as e:
        print('Retry connection', e)
        time.sleep(10)


if __name__ == '__main__':
    while True:
        run()
