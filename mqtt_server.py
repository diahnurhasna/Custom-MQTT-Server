import socket
import threading
from influxdb import InfluxDBClient
import struct
from collections import defaultdict


class MQTTServer:
    def __init__(self, host='0.0.0.0', port=1883):
        self.host = host
        self.port = port
        self.clients = {}
        self.topics = defaultdict(set)
        self.influx_client = InfluxDBClient(host='localhost', port=8086, database='mqtt_data') 
        self.influx_client.create_database('mqtt_data')  # Create if it doesn't exist

    def handle_client(self, client_socket, address):
        print(f"[NEW CONNECTION] {address} connected.")
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                packet_type = self.parse_packet_type(data[0])

                if packet_type == "CONNECT":
                    self.handle_connect(client_socket, data, address)
                elif packet_type == "PUBLISH":
                    self.handle_publish(client_socket, data)
                elif packet_type == "SUBSCRIBE":
                    self.handle_subscribe(client_socket, data, address)
                elif packet_type == "PINGREQ":
                    self.handle_pingreq(client_socket)
                elif packet_type == "DISCONNECT":
                    self.handle_disconnect(client_socket, address)
                    break
                else:
                    print(f"[UNKNOWN PACKET TYPE] {packet_type}")

        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            self.remove_client(client_socket, address)
            client_socket.close()

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"[LISTENING] Server is listening on {self.host}:{self.port}")

        while True:
            client, addr = server.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client, addr))
            client_thread.start()

    def parse_packet_type(self, byte):
        packet_types = {
            1: "CONNECT",
            3: "PUBLISH",
            8: "SUBSCRIBE",
            12: "PINGREQ",
            14: "DISCONNECT"
        }
        try:
            return packet_types[(byte >> 4) & 0xF]
        except KeyError:
            return "UNKNOWN"

    def handle_connect(self, client_socket, data, address):
        # Verify packet length
        if len(data) < 12:  # Minimum CONNECT packet length
            print("[ERROR] CONNECT packet too short")
            return

        # Extract client ID length and value from the payload
        protocol_name_len = struct.unpack("!H", data[2:4])[0]
        protocol_name = data[4:4 + protocol_name_len].decode('utf-8')

        # Make sure it's the MQTT protocol
        if protocol_name != "MQTT":
            print("[ERROR] Unsupported protocol name")
            return

        # Parse keep-alive and client ID
        client_id_len = struct.unpack("!H", data[10:12])[0]
        client_id = data[12:12 + client_id_len].decode('utf-8')
        self.clients[client_socket] = {"id": client_id, "address": address}

        # Send CONNACK response
        connack_packet = b'\x20\x02\x00\x00'
        client_socket.sendall(connack_packet)
        print(f"[CONNECT] Client {client_id} connected.")


    def handle_publish(self, client_socket, data):
        # Parse topic length and name
        topic_length = struct.unpack("!H", data[2:4])[0]
        topic = data[4:4 + topic_length].decode('utf-8')
        
        # Calculate payload start index, accounting for QoS > 0
        payload_start = 4 + topic_length
        if len(data) > payload_start:
            payload = data[payload_start:].decode('utf-8')
            print(f"[PUBLISH] Topic: {topic}, Payload: {payload}")

            # Store data in InfluxDB
            self.influx_client.write_points([{"measurement": topic, "fields": {"value": payload}}])

            # Deliver message to subscribed clients
            self.publish_to_subscribers(topic, payload)
        else:
            print("[ERROR] Invalid PUBLISH packet structure")



    def handle_subscribe(self, client_socket, data, address):
        # ... (Extract topic filters, QoS levels, etc.) ...
        packet_id = struct.unpack("!H", data[2:4])[0]
        topic_length = struct.unpack("!H", data[4:6])[0]
        topic = data[6:6 + topic_length].decode('utf-8')
        qos = data[6 + topic_length]

        self.topics[topic].add(client_socket)
        print(f"[SUBSCRIBE] {self.clients[client_socket]['id']} subscribed to {topic} with QoS {qos}")

        # ... (Send SUBACK packet) ...
        suback_packet = struct.pack("!BBBH", 9, 2, packet_id, qos)
        client_socket.sendall(suback_packet)

    def handle_pingreq(self, client_socket):
        # ... (Send PINGRESP packet) ...
        pingresp_packet = b'\xd0\x00'
        client_socket.sendall(pingresp_packet)

    def handle_disconnect(self, client_socket, address):
        print(f"[DISCONNECT] {address} disconnected.")
        self.remove_client(client_socket, address)

    def remove_client(self, client_socket, address):
        if client_socket in self.clients:
            client_id = self.clients[client_socket]['id']
            del self.clients[client_socket]
            for topic in self.topics:
                if client_socket in self.topics[topic]:
                    self.topics[topic].remove(client_socket)
            print(f"[CLIENT REMOVED] {client_id} removed.")

    def publish_to_subscribers(self, topic, payload):
        for client in self.topics[topic]:
            try:
                # ... (Construct PUBLISH packet) ...
                publish_packet = self.create_publish_packet(topic, payload)
                client.sendall(publish_packet)
            except:
                print(f"[ERROR] Failed to send message to client.")

    def create_publish_packet(self, topic, payload):
        # ... (Construct PUBLISH packet with appropriate headers, QoS, etc.) ...
        # This is a simplified example, QoS and other features need to be implemented
        topic_length = len(topic)
        payload_length = len(payload)
        fixed_header = 0x30  # PUBLISH packet type with QoS 0
        remaining_length = topic_length + payload_length + 2  # +2 for topic length field

        packet = bytearray()
        packet.append(fixed_header << 4)  # Packet type and flags
        packet.extend(self.encode_remaining_length(remaining_length))
        packet.extend(struct.pack("!H", topic_length))
        packet.extend(topic.encode('utf-8'))
        packet.extend(payload.encode('utf-8'))
        return packet

    def decode_remaining_length(self, client_socket):
        multiplier = 1
        value = 0
        while True:
            encoded_byte = client_socket.recv(1)[0]
            value += (encoded_byte & 127) * multiplier
            if (encoded_byte & 128) == 0:
                break
            multiplier *= 128
        return value


if __name__ == "__main__":
    server = MQTTServer()
    server.start()
