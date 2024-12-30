import socket
import json
import re
import datetime
from cachetools import cached, LRUCache
from threading import Lock
from src.bases.error.client import ClientError


class SingletonSocket:
    """A thread-safe Singleton implementation for managing a single socket connection."""
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(SingletonSocket, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, host, port, timeout=10):
        if not self._initialized:
            self.host = host
            self.port = port
            self.timeout = timeout
            self.socket = None
            self._initialized = True
            self._connect()

    @staticmethod
    def mapping_payload(packet_type, packet_id, body_format_type, body):
        """Creates a TCCP packet string."""
        stx = '\x02'  # Start of text character
        etx = '\x03'  # End of text character
        protocol_id = '02'
        qos = '0'
        tx_type = 'O'  # Application
        tx_id = '00000'
        rx_type = 'C'  # Central Unit
        rx_id = '00000'
        tx_prop = '0'
        tx_session = '0'
        room_id = '000'

        header = f"{protocol_id}:{packet_type}{packet_id}{body_format_type}{qos}{tx_type}{tx_id}{rx_type}{rx_id}{tx_prop}{tx_session}{room_id}"
        packet_length = len(header) + len(body) + 2  # header + body + stx + etx
        packet = f"{stx}{header}{packet_length:04d}:{body}{etx}"  # format packet length to 4 digits
        return packet

    def _connect(self):
        """Establish a new socket connection."""
        self.close()  # Close existing socket if any
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))

            connect_body = {
                "typ": "Application",
                "nam": "DU",
                "ver": "1.01",
                "inf": "",
                "svr": 0,
                "tim": datetime.datetime.now().isoformat()
            }
            json_body = json.dumps(connect_body)
            connect_packet = self.mapping_payload('con', '0001', '02', json_body)

            try:
                self.send(connect_packet)
                reply = self.receive(1024)
                if "rep" not in reply:
                    raise ClientError(message="Failed to establish connection.", meta=reply)
                print("Connection established successfully.")
            except Exception as e:
                raise ClientError(message="Error during connection.", meta=str(e))

            print("Socket connected successfully.")
        except Exception as e:
            self.socket = None
            raise ClientError(message='Cannot connect to socket', meta=str(e))

    def send(self, data):
        """Send data through the socket. Reconnect if needed."""
        try:
            if self.socket is None:
                print("Reconnecting socket...")
                self._connect()
            self.socket.sendall(data.encode('ascii'))
        except Exception as e:
            print(f"Error sending data: {e}")
            print("Attempting to reconnect and resend...")
            self._connect()
            self.socket.sendall(data.encode('ascii'))

    def receive(self, buffer_size=1024):
        """Receive data from the socket. Reconnect if needed."""
        try:
            if self.socket is None:
                print("Reconnecting socket...")
                self._connect()
            return self.socket.recv(buffer_size).decode('ascii')
        except Exception as e:
            print(f"Error receiving data: {e}")
            print("Attempting to reconnect...")
            self._connect()
            return self.socket.recv(buffer_size).decode('ascii')

    def close(self):
        """Close the socket if it exists."""
        if self.socket:
            try:
                self.socket.close()
                self.socket = None
                print("Socket connection closed.")
            except Exception as e:
                print(f"Error closing socket: {e}")


class DcernoClient:
    def __init__(self, host, port, timeout=10):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket_manager = SingletonSocket(host, port, timeout)

    def connect(self):
        connect_body = {
            "typ": "Application",
            "nam": "DU",
            "ver": "1.01",
            "inf": "",
            "svr": 0,
            "tim": datetime.datetime.now().isoformat()
        }
        json_body = json.dumps(connect_body)
        connect_packet = self.mapping_payload('con', '0001', '02', json_body)

        try:
            self.socket_manager.send(connect_packet)
            reply = self.socket_manager.receive(1024)
            if "rep" not in reply:
                raise ClientError(message="Failed to establish connection.", meta=reply)
            print("Connection established successfully.")
        except Exception as e:
            raise ClientError(message="Error during connection.", meta=str(e))

    def get_all_units(self):
        """Retrieves all units from the D-Cerno system."""

        try:
            # Create a get packet for retrieving all units
            get_units_body = {
                "nam": "gunits"
            }
            json_body = json.dumps(get_units_body)
            get_units_packet = self.mapping_payload('get', '0002', '02', json_body)  # packet ID is 0002
            print(f"Sending get all units packet: {get_units_packet}")

            # Send the packet
            self.socket_manager.send(get_units_packet)

            # Receive and handle the reply
            reply = self.socket_manager.receive(1024)
            print(f"Received reply: {reply}")
            if reply:
                print("Successfully retrieved all units.")
                if 'micstat' in reply and 'units' not in reply:
                    json_data = re.search(r'{.*}', reply, re.DOTALL).group()
                    parsed_data = json.loads(json_data)
                    if parsed_data.get('nam') == 'micstat':
                        return {
                            'nam': parsed_data.get('nam'),
                            's': [
                                dict(uid=parsed_data.get('uid'), stat=parsed_data.get('stat'))
                            ]
                        }
                else:
                    pattern = r'02:[a-zA-Z0-9]+:\{\s*("nam":\s*"units",\s*"s":\s*\[.*?\])\s*\}'
                    matches = re.finditer(pattern, reply, re.DOTALL)
                    for match in matches:
                        try:
                            # Extract and parse the JSON
                            parsed_data = "{" + match.group(1) + "}"
                            parsed_data = json.loads(parsed_data)
                            return parsed_data
                        except Exception as e:
                            print('Cannot decode reply get unit', e)
            raise ClientError(message="Error retrieving all units.")
        except Exception as e:
            raise ClientError(message=f"Error retrieving all units: {e}")

    @staticmethod
    def mapping_payload(packet_type, packet_id, body_format_type, body):
        """Creates a TCCP packet string."""
        stx = '\x02'  # Start of text character
        etx = '\x03'  # End of text character
        protocol_id = '02'
        qos = '0'
        tx_type = 'O'  # Application
        tx_id = '00000'
        rx_type = 'C'  # Central Unit
        rx_id = '00000'
        tx_prop = '0'
        tx_session = '0'
        room_id = '000'

        header = f"{protocol_id}:{packet_type}{packet_id}{body_format_type}{qos}{tx_type}{tx_id}{rx_type}{rx_id}{tx_prop}{tx_session}{room_id}"
        packet_length = len(header) + len(body) + 2  # header + body + stx + etx
        packet = f"{stx}{header}{packet_length:04d}:{body}{etx}"  # format packet length to 4 digits
        return packet

    def get_microphone_status(self, uid='0'):
        """Retrieves the microphone status from the D-Cerno system."""
        try:
            # Create a get packet for retrieving microphone status
            get_mic_status_body = {
                "nam": "gmicstat",
                "uid": uid  # '0' for all microphones, or a specific serial
            }
            json_body = json.dumps(get_mic_status_body)
            get_mic_status_packet = self.mapping_payload('get', '0003', '02', json_body)  # packet ID is 0002
            print(f"Sending get microphone status packet: {get_mic_status_packet}")

            # Send the packet
            self.socket_manager.send(get_mic_status_packet)

            # Receive and handle the reply
            reply = self.socket_manager.receive(1024)
            print(f"Received reply: {reply}")

            if reply:
                json_data = re.search(r'{.*}', reply, re.DOTALL).group()
                parsed_data = json.loads(json_data)
                return parsed_data
            raise ClientError(message="Error retrieving microphone status.")
        except Exception as e:
            raise ClientError(message=f"Error retrieving microphone status: {e}")


if __name__ == "__main__":
    d = DcernoClient(host='192.168.0.20', port=5011)
    units = d.get_all_units()
    for unit in units['s']:
        unit_info = d.get_microphone_status(unit['uid'])  # get status for all mics
        print(unit_info)
