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

    try:
        client = DcernoClient(
            host=DCERNO_CONFIG['host'],
            port=DCERNO_CONFIG['port'],
            timeout=5
        )
        ips = VHD_CONFIG['ips']
        current_active_micros = {}
        for ip in ips:
            current_active_micros[ip] = {}

        while True:
            time.sleep(1)
            print('====CHECKING camera=====')
            if not os.path.exists(DECERNO_VHD_SETTING_PATH):
                with open(DECERNO_VHD_SETTING_PATH, 'w') as f:
                    json.dump({}, f)
            settings = json.load(open(DECERNO_VHD_SETTING_PATH, 'r')) or {}
            tracking_enabled = {}
            for ip, enable in settings.items():
                if enable:
                    tracking_enabled[ip] = enable
                    current_active_micros[ip]['auto_tracking'] = True

            if not os.path.exists(DECERNO_VHD_MAPPING_PATH):
                with open(DECERNO_VHD_MAPPING_PATH, 'w') as f:
                    json.dump({}, f)

            dcerno_mapping = json.load(open(DECERNO_VHD_MAPPING_PATH, 'r')) or {}
            if not dcerno_mapping:
                continue
            try:
                data = client.get_all_units()
            except:
                continue
            active_micros = {}
            for micro in data['s']:
                if micro.get('stat') == '1':
                    micro_id = micro['uid']
                    m = dcerno_mapping.get(micro_id)
                    if not m:
                        continue
                    active_micros[micro_id] = m

            for camera_ip, micro_info in current_active_micros.items():
                active_micro_id = micro_info.get('micro_id')
                if active_micro_id:
                    if active_micro_id not in active_micros:
                        vhd_client = VHDClient(uri=camera_ip, logger=logger)
                        try:
                            vhd_client.call(
                                action='home',
                                position='10',
                                zoom='10',
                            )
                        except:
                            pass
                        current_active_micros[camera_ip] = {}
                    else:
                        continue
                else:
                    if not micro_info.get('auto_tracking'):
                        continue
                    for micro_id, active_micro in active_micros.items():
                        if active_micro['camera_ip'] == camera_ip:
                            position = active_micro['number']
                            camera_ip = active_micro['camera_ip']
                            print(f'set {current_active_micro} active')
                            vhd_client = VHDClient(uri=camera_ip, logger=logger)
                            vhd_client.call(
                                action='poscall',
                                position=str(position),
                            )
                            current_active_micros[camera_ip] = active_micro
                            break
    except Exception as e:
        print('Retry connection', e)
        time.sleep(10)


if __name__ == '__main__':
    while True:
        run()
