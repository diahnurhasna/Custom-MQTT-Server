import socket
import threading
from influxdb import InfluxDBClient
import struct
from collections import defaultdict


class MQTTServer:
    def __init__(self, host='0.0.0.0', port=1884):
        self.host = host
        self.port = port
        self.clients = {}
        self.topics = defaultdict(set)
        self.use_influx = True  # Flag to check if InfluxDB is available

        # Attempt to connect to InfluxDB
        try:
            self.influx_client = InfluxDBClient(host='localhost', port=8086, database='mqtt_data')
            self.influx_client.create_database('mqtt_data')  # Create if it doesn't exist
            print("[INFO] Connected to InfluxDB")
        except Exception as e:
            print(f"[ERROR] InfluxDB connection failed: {e}")
            self.use_influx = False  # Disable InfluxDB usage if there's an error

    def handle_client(self, client_socket, address):
        print(f"[NEW CONNECTION] {address} connected.")
        try:
            buffer = b""
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                buffer += data

                # Check if we've received enough data for at least the fixed header
                if len(buffer) < 2:
                    continue  # Wait for more data

                # Read the packet type and remaining length from the fixed header
                packet_type = (buffer[0] >> 4) & 0x0F
                remaining_length = buffer[1]

                # Wait until we have the full packet based on remaining length
                total_length = 2 + remaining_length
                if len(buffer) < total_length:
                    continue  # Wait for more data

                # Process the packet based on packet type
                packet_data = buffer[:total_length]
                buffer = buffer[total_length:]  # Remove the processed packet from buffer

                if packet_type == 1:  # CONNECT
                    self.handle_connect(client_socket, packet_data, address)
                elif packet_type == 3:  # PUBLISH
                    self.handle_publish(client_socket, packet_data)
                elif packet_type == 8:  # SUBSCRIBE
                    self.handle_subscribe(client_socket, packet_data, address)
                elif packet_type == 12:  # PINGREQ
                    self.handle_pingreq(client_socket)
                elif packet_type == 14:  # DISCONNECT
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
            0x10: "CONNECT",
            0x30: "PUBLISH",
            0x80: "SUBSCRIBE",
            0xC0: "PINGREQ",
            0xE0: "DISCONNECT"
        }
        return packet_types.get(byte & 0xF0, "UNKNOWN")


    def handle_connect(self, client_socket, data, address):
        try:
            # Check for minimum length
            if len(data) < 10:  # Basic check for minimum length
                print("[ERROR] CONNECT packet too short")
                return

            # Check packet type (should be 0x10 for CONNECT)
            packet_type = (data[0] >> 4) & 0x0F
            if packet_type != 1:
                print(f"[ERROR] Expected CONNECT packet, but got type {packet_type}")
                return

            # Parse protocol name length
            protocol_name_len = struct.unpack("!H", data[2:4])[0]
            protocol_name = data[4:4 + protocol_name_len].decode('utf-8')
            print(f"[CONNECT] Protocol Name: {protocol_name}")

            # Verify protocol name is "MQTT"
            if protocol_name != "MQTT":
                print(f"[ERROR] Unsupported protocol name: {protocol_name}")
                return

            # Parse protocol level (should be 4 for MQTT 3.1.1 or 5 for MQTT 5.0)
            protocol_level = data[4 + protocol_name_len]
            if protocol_level not in [4, 5]:
                print(f"[ERROR] Unsupported MQTT protocol level: {protocol_level}")
                return

            # Parse Client ID
            client_id_len = struct.unpack("!H", data[10:12])[0]
            client_id = data[12:12 + client_id_len].decode('utf-8')
            print(f"[CONNECT] Client ID: {client_id}")

            # Register the client
            self.clients[client_socket] = {"id": client_id, "address": address}

            # Send CONNACK response
            connack_packet = b'\x20\x02\x00\x00'
            client_socket.sendall(connack_packet)
            print(f"[CONNECT] Client {client_id} connected successfully.")

        except Exception as e:
            print(f"[ERROR] in handle_connect: {e}")



    def handle_publish(self, client_socket, data):
        topic_length = struct.unpack("!H", data[2:4])[0]
        topic = data[4:4 + topic_length].decode('utf-8')

        payload_start = 4 + topic_length
        if len(data) > payload_start:
            payload = data[payload_start:].decode('utf-8')
            print(f"[PUBLISH] Topic: {topic}, Payload: {payload}")

            if self.use_influx:
                try:
                    self.influx_client.write_points([{"measurement": topic, "fields": {"value": payload}}])
                except Exception as e:
                    print(f"[ERROR] Failed to write to InfluxDB: {e}")
                    self.use_influx = False  # Disable InfluxDB if an error occurs during a write

            self.publish_to_subscribers(topic, payload)
        else:
            print("[ERROR] Invalid PUBLISH packet structure")

    def handle_subscribe(self, client_socket, data, address):
        try:
            print(f"[DEBUG] Raw data for subscription: {data}")
            packet_id = struct.unpack("!H", data[2:4])[0]
            topic_length = struct.unpack("!H", data[4:6])[0]

            if len(data) < 6 + topic_length:
                print("[ERROR] Subscription data is too short.")
                return

            topic = data[6:6 + topic_length].decode('utf-8')
            qos = data[6 + topic_length]

            self.topics[topic].add(client_socket)
            print(f"[SUBSCRIBE] {self.clients[client_socket]['id']} subscribed to {topic} with QoS {qos}")

            suback_packet = struct.pack("!BBH", 9, 2, packet_id)  # Packet type, return code, and packet ID
            client_socket.sendall(suback_packet)

        except Exception as e:
            print(f"[ERROR] In handle_subscribe: {e}")
            self.remove_client(client_socket, address)

    def handle_pingreq(self, client_socket):
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
        print(f"[PUBLISH TO SUBSCRIBERS] Topic: {topic}, Payload: {payload}")
        for client in self.topics[topic]:
            try:
                publish_packet = self.create_publish_packet(topic, payload)
                client.sendall(publish_packet)
            except:
                print(f"[ERROR] Failed to send message to client.")

    def create_publish_packet(self, topic, payload):
        topic_length = len(topic)
        payload_length = len(payload)
        fixed_header = 0x30  # PUBLISH packet type with QoS 0
        remaining_length = topic_length + payload_length + 2  # +2 for topic length field

        packet = bytearray()
        packet.append(fixed_header << 4)
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
