from src.bases.api.routes import RouteLogicHandler
from src.clients.dcerno import DcernoClient
from src.clients.vhd import VHDClient
from src.bases.error.client import ClientError
from config import DCERNO_CONFIG, VHD_CONFIG


class MicrophonesPingLogicHandler(RouteLogicHandler):
    def run(self):
        mic_ping = False
        try:
            client = DcernoClient(
                host=DCERNO_CONFIG['host'],
                port=DCERNO_CONFIG['port'],
                timeout=2
            )
            if client.get_all_units():
                mic_ping = True
        except ClientError as e:
            pass
        cam_pings = []
        for ip in VHD_CONFIG['ips']:
            p = False
            try:
                client = VHDClient(
                    uri=ip,
                    logger=self.logger
                )
                res = client.ping()
                p = True
            except Exception as e:
                pass
            cam_pings.append(dict(ip=ip, ping=p))

        return dict(mic_ping=mic_ping, cam_pings=[{cam_pings}])