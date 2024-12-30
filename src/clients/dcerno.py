import socket
import json
import re
import datetime
from cachetools import cached, LRUCache

from src.bases.error.client import ClientError


class DcernoClient():
    socket = None

    def __init__(self, host, port, timeout=10):
        self.host = host
        self.port = port

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

    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        try:
            s.connect((self.host, self.port))
        except Exception as e:
            raise ClientError(message='Cannot connect microphone', meta=str(e))

        connect_body = {
            "typ": "Application",
            "nam": "DU",
            "ver": "1.01",
            "inf": "",
            "svr": 0,
            "tim": datetime.datetime.now().isoformat()
        }

        # Convert the body to JSON format
        json_body = json.dumps(connect_body)
        connect_packet = self.mapping_payload('con', '0001', '02', json_body)

        # Send the packet
        try:
            s.sendall(connect_packet.encode('ascii'))
            reply = s.recv(1024).decode('ascii')
        except Exception as e:
            raise ClientError(message='Cannot send connect packet', meta=str(e))
        # Receive and handle the reply

        # Process the reply
        if reply and "rep" in reply:
            return s
        else:
            raise ClientError("Connection established successfully", meta=reply)

    def disconnect(self, socket, disconnect_id='00', disconnect_info='Normal disconnect'):
        """Disconnects from the D-Cerno system."""
        try:
            # Create a disconnect packet (dis)
            disconnect_body = {
                "id": disconnect_id,
                "inf": disconnect_info,
                "svr": 0
            }
            json_body = json.dumps(disconnect_body)
            disconnect_packet = create_tccp_packet('dis', '0004', '02', json_body)  # packet ID is 0003
            print(f"Sending disconnect packet: {disconnect_packet}")
            # Send the disconnect packet
            socket.sendall(disconnect_packet.encode('ascii'))

            print("Disconnected from D-Cerno system.")
        except Exception as e:
            print(f"Error during disconnection: {e}")

    def get_all_units(self):
        """Retrieves all units from the D-Cerno system."""
        socket = self.connect()

        try:
            # Create a get packet for retrieving all units
            get_units_body = {
                "nam": "gunits"
            }
            json_body = json.dumps(get_units_body)
            get_units_packet = self.mapping_payload('get', '0002', '02', json_body)  # packet ID is 0002
            print(f"Sending get all units packet: {get_units_packet}")

            # Send the packet
            socket.sendall(get_units_packet.encode('ascii'))

            # Receive and handle the reply
            reply = socket.recv(1024).decode('ascii')
            print(f"Received reply: {reply}")
            self.disconnect(socket)
            if reply:
                if "rep" in reply:
                    print("Successfully retrieved all units.")
                    json_data = re.search(r'{.*}', reply, re.DOTALL).group()
                    parsed_data = json.loads(json_data)
                    return parsed_data
            raise ClientError(message="Error retrieving all units.")
        except Exception as e:
            raise ClientError(message=f"Error retrieving all units: {e}")

    def get_microphone_status(self, uid='0'):
        socket = self.connect()
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
            socket.sendall(get_mic_status_packet.encode('ascii'))

            # Receive and handle the reply
            reply = socket.recv(1024).decode('ascii')
            print(f"Received reply: {reply}")
            self.disconnect(socket)

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
