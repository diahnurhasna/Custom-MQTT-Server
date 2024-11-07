import network
import time
from umqtt.simple import MQTTClient
import machine
import urandom  # Import urandom for random number generation

# Wi-Fi configuration
WIFI_SSID = 'Wokwi-GUEST'
WIFI_PASSWORD = ''

# MQTT broker configuration
MQTT_BROKER = '109.110.188.37'
MQTT_PORT = 1884 # Typically 1883 for non-SSL connections
MQTT_TOPIC = 'sensor/data'  # Replace with your topic

# Function to connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        time.sleep(1)
    print("Connected to Wi-Fi:", wlan.ifconfig())

# Function to connect and publish to MQTT
def mqtt_publish():
    client = MQTTClient('esp32_publisher', MQTT_BROKER, port=MQTT_PORT)
    try:
        client.connect()
        print("Connected to MQTT broker")
    except OSError as e:
        print("Failed to connect to MQTT broker:", e)
        return

    # Publish data in a loop
    while True:
        # Simulate sensor data using urandom
        temperature = 25 + urandom.getrandbits(4) % 10  # Random temperature between 25-34
        humidity = 50 + urandom.getrandbits(4) % 10     # Random humidity between 50-59

        # Create payload
        payload = f'{{"temperature": {temperature}, "humidity": {humidity}}}'
        
        try:
            client.publish(MQTT_TOPIC, payload)
            print("Published:", payload)
        except OSError as e:
            print("Failed to publish message:", e)

        # Wait before sending the next message
        time.sleep(1)  # Publish every 10 seconds

# Main execution
try:
    connect_wifi()
    mqtt_publish()
except KeyboardInterrupt:
    print("Program interrupted")
