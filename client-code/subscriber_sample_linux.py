import paho.mqtt.client as mqtt

# MQTT broker configuration
MQTT_BROKER = '109.110.188.37'
MQTT_PORT = 1883  # Typically 1883 for non-SSL connections
MQTT_TOPIC = 'sensor/data'

# Callback function for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully!")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print("Failed to connect. Return code:", rc)

# Callback function for when the client receives a message
def on_message(client, userdata, message):
    print("Received message:")
    print("Topic:", message.topic)
    print("Payload:", message.payload.decode())

# Set up the MQTT client
client = mqtt.Client("linux_subscriber")
client.on_connect = on_connect
client.on_message = on_message

try:
    # Connect to the broker
    client.connect(MQTT_BROKER, MQTT_PORT)
    print("Attempting to connect to broker...")

    # Start the loop to process callbacks and keep the client connected
    client.loop_forever()

except KeyboardInterrupt:
    print("Disconnecting from broker...")
    client.disconnect()
    print("Disconnected successfully.")
except Exception as e:
    print("An error occurred:", e)
