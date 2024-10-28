# MQTT Server with InfluxDB Integration

This project implements a simple **MQTT server** in Python, supporting essential MQTT operations such as `CONNECT`, `PUBLISH`, `SUBSCRIBE`, and `PINGREQ`. The server stores published data in an **InfluxDB** database and distributes messages to subscribed clients. 

---

## Features
- **MQTT protocol** support for `CONNECT`, `PUBLISH`, `SUBSCRIBE`, `PINGREQ`, and `DISCONNECT`.
- **Multi-client handling** using Python threads.
- **InfluxDB integration** to store published topic data.
- Support for **QoS level 0** (best-effort delivery).
- **Topic-based message delivery** to subscribed clients.

---

## Prerequisites

1. **Python 3.x** installed  
2. Install required Python packages:
   ```bash
   pip install influxdb
   ```

3. **InfluxDB** server running on `localhost` with port `8086`.

4. Create the InfluxDB database:
   ```bash
   influx
   CREATE DATABASE mqtt_data
   ```

---

## Setup and Usage

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. **Run the MQTT server:**
   ```bash
   python mqtt_server.py
   ```

3. The server will listen on `0.0.0.0:1883` by default:
   ```
   [LISTENING] Server is listening on 0.0.0.0:1883
   ```

---

## Code Overview

### `MQTTServer` Class
- **`__init__`**: Initializes the server, InfluxDB client, and data structures for clients and topics.
- **`start()`**: Starts the server and listens for incoming client connections.
- **`handle_client()`**: Manages individual client connections and processes MQTT packets.
- **`parse_packet_type()`**: Decodes the packet type from incoming data.
- **`handle_connect()`**: Processes `CONNECT` packets and sends `CONNACK` responses.
- **`handle_publish()`**: Processes `PUBLISH` packets, stores data in InfluxDB, and sends messages to subscribers.
- **`handle_subscribe()`**: Manages client subscriptions to topics.
- **`publish_to_subscribers()`**: Sends messages to clients subscribed to a specific topic.
- **`create_publish_packet()`**: Builds MQTT `PUBLISH` packets.
- **`handle_pingreq()`**: Responds to `PINGREQ` packets.
- **`handle_disconnect()`**: Handles client disconnection and resource cleanup.

---

## Example Workflow

1. A client sends a `CONNECT` packet to the server.
2. Upon successful connection, the client subscribes to a topic.
3. Another client publishes a message to the subscribed topic.
4. The message is stored in **InfluxDB** and forwarded to the subscribers.

---

## Error Handling

- Invalid packets are logged with `[ERROR]`.
- Unknown packet types are logged with `[UNKNOWN PACKET TYPE]`.
- Client disconnections are handled gracefully to free resources.

---

## Dependencies

- **Python 3.x**
- **InfluxDB Python Client**:  
  Install via:
  ```bash
  pip install influxdb
  ```

---

## Contributing

Feel free to open issues or submit pull requests to improve this MQTT server!

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

---

## Contact

For any questions or issues, please contact the project maintainer.

---

Enjoy using the MQTT server! 🚀
