import network
import socket
import struct
import time

# Wi-Fi and server configuration
SSID = 'Wokwi-GUEST'
PASSWORD = ''
MQTT_SERVER = '109.110.188.37'  # Replace with the IP address of your MQTT server
MQTT_PORT = 1883
CLIENT_ID = 'esp32_client'
PUBLISH_TOPIC = 'your_publish_topic'  # Replace with the topic you want to publish to
KEEP_ALIVE = 60  # MQTT keep-alive time in seconds

# Wi-Fi connection setup
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        time.sleep(1)
    print("Connected to Wi-Fi:", wlan.ifconfig())

# Manually construct an MQTT CONNECT packet
def create_connect_packet(client_id):
    packet_type = 0x10  # MQTT packet type for CONNECT
    protocol_name = b'\x00\x04MQTT'  # Protocol name
    protocol_level = b'\x04'  # Protocol level for MQTT 3.1.1
    connect_flags = b'\x02'  # Clean session flag
    keep_alive = struct.pack("!H", KEEP_ALIVE)  # Keep-alive time
    client_id_bytes = client_id.encode('utf-8')
    client_id_length = struct.pack("!H", len(client_id_bytes))
    variable_header = protocol_name + protocol_level + connect_flags + keep_alive
    payload = client_id_length + client_id_bytes
    remaining_length = len(variable_header) + len(payload)
    fixed_header = struct.pack("!BB", packet_type, remaining_length)
    return fixed_header + variable_header + payload

# Manually construct an MQTT PUBLISH packet
def create_publish_packet(topic, message):
    packet_type = 0x30  # MQTT packet type for PUBLISH
    topic_bytes = topic.encode('utf-8')
    topic_length = struct.pack("!H", len(topic_bytes))
    message_bytes = message.encode('utf-8')
    remaining_length = len(topic_bytes) + len(message_bytes) + 2
    fixed_header = struct.pack("!BB", packet_type, remaining_length)
    return fixed_header + topic_length + topic_bytes + message_bytes

# Connect to the MQTT server and send the CONNECT packet
def connect_mqtt():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((MQTT_SERVER, MQTT_PORT))
    print("Connected to MQTT server")

    connect_packet = create_connect_packet(CLIENT_ID)
    client_socket.sendall(connect_packet)
    print("Sent CONNECT packet")

    # Wait for CONNACK response
    connack = client_socket.recv(4)
    if connack == b'\x20\x02\x00\x00':  # CONNACK success
        print("Received CONNACK - Connected successfully!")
    else:
        print("Failed to connect: CONNACK packet error")

    return client_socket

# Publish a message to the MQTT server
def publish_message(client_socket, topic, message):
    publish_packet = create_publish_packet(topic, message)
    client_socket.sendall(publish_packet)
    print(f"Published message: {message} on topic: {topic}")

# Main function to set up Wi-Fi, connect to MQTT, and publish data
def main():
    connect_wifi()
    client_socket = connect_mqtt()
    
    try:
        while True:
            message = "AYANG DIAH MANISS"  # Message to be sent
            publish_message(client_socket, PUBLISH_TOPIC, message)
            time.sleep(5)  # Delay between messages
    except KeyboardInterrupt:
        client_socket.close()
        print("Disconnected from MQTT server")

# Run the main function
main()
