import yaml
import os

ROOT_PATH = os.path.dirname(__file__)

CONFIG_FILE_PATH = os.path.join(ROOT_PATH, 'env.yaml')

if os.path.exists(CONFIG_FILE_PATH):
    with open(CONFIG_FILE_PATH, 'r') as r_file:
        data = yaml.safe_load(r_file)
else:
    data = dict()

ENVIRONMENT = data.get('ENVIRONMENT', 'local')

SECRET_KEY = data.get('SECRET_KEY', 'secret_key')

VERSION = data.get('VERSION', 'v1')

MONGO_URI = data.get('MONGO_URI', 'mongodb://localhost:31279')
MONGO_DB_NAME = data.get('MONGO_DB_NAME', 'camera_tracking')
SENTRY_DNS = data.get('SENTRY_DNS', '')

REDIS = data.get('REDIS', dict(
    password='813417',
    host='localhost',
    port=6379,
))

DCERNO_CONFIG = data.get(
    'DCERNO_CONFIG', dict(
        host='192.168.0.20',
        port=5011
    )
)


class CeleryConfig(object):
    env = ENVIRONMENT

    broker_url = 'redis://:{password}@{host}:{port}/{db}'.format(
        password=REDIS['password'],
        host=REDIS['host'],
        port=REDIS['port'],
        db=0,
    )

    sentry_dns = SENTRY_DNS


class ApiConfig(object):
    APP_NAME = 'Camera Tracking'

    ENV = ENVIRONMENT

    SECRET_KEY = SECRET_KEY

    SENTRY_DNS = SENTRY_DNS
