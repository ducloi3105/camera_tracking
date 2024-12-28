from pathlib import Path
import os
import json
import time
import logging

from src.clients.dcerno import DcernoClient
from src.clients.vhd import VHDClient
from src.bases.error.client import ClientError
from config import DCERNO_CONFIG, VHD_CONFIG

logger = logging.getLogger()


def run():
    dcerno_config_path = os.path.join(Path.home() / 'Documents', 'decerno_vhd_config.json')
    setting_config_path = os.path.join(Path.home() / 'Documents', 'decerno_vhd_settings.json')
    micro_active = None
    vhd_client = VHDClient(uri=VHD_CONFIG['uri'], logger=logger)
    while True:
        time.sleep(1)
        settings = json.load(open(setting_config_path, 'r')) or {}
        if not settings.get('tracking_enabled'):
            continue

        micro_settings = json.load(open(dcerno_config_path, 'r')) or {}
        if not micro_settings:
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
        if active_mic != micro_active:
            micro_active = active_mic

        position = micro_settings.get(micro_active)
        if not position:
            continue

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
