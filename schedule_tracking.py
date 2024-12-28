from pathlib import Path
import os
import json


def run():
    config_path = os.path.join(Path.home() / 'Documents', 'decerno_vhd_settings.json')
    while True:
        settings = json.load(open(config_path, 'r'))


if __name__ == '__main__':
    run()