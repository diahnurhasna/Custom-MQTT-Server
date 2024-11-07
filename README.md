---

# MQTT Server with InfluxDB Integration

This project implements a simple **MQTT server** in Python, supporting essential MQTT operations like `CONNECT`, `PUBLISH`, `SUBSCRIBE`, and `PINGREQ`. The server stores published data in an **InfluxDB** database and distributes messages to subscribed clients.

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

## TODO

- **Node-Red integration**: Enable seamless IoT workflow management and visualization through **Node-Red**.
- **Adding LSTM Algorithm**: Integrate a **Long Short-Term Memory (LSTM)** neural network to predict resource usage and scale system resources dynamically based on the incoming data patterns.

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

---

# Server MQTT dengan Integrasi InfluxDB (Bahasa Indonesia)

Proyek ini mengimplementasikan **server MQTT** sederhana menggunakan Python, yang mendukung operasi MQTT dasar seperti `CONNECT`, `PUBLISH`, `SUBSCRIBE`, dan `PINGREQ`. Server ini menyimpan data yang dipublikasikan di **database InfluxDB** dan mendistribusikan pesan ke klien yang berlangganan.

---

## Fitur
- Dukungan protokol **MQTT** untuk `CONNECT`, `PUBLISH`, `SUBSCRIBE`, `PINGREQ`, dan `DISCONNECT`.
- **Penanganan multi-klien** menggunakan thread Python.
- **Integrasi InfluxDB** untuk menyimpan data topik yang dipublikasikan.
- Dukungan untuk **QoS level 0** (pengiriman terbaik).
- Pengiriman pesan berbasis **topik** ke klien yang berlangganan.

---

## Prasyarat

1. **Python 3.x** telah terinstal  
2. Instal paket Python yang diperlukan:
   ```bash
   pip install influxdb
   ```

3. Server **InfluxDB** berjalan pada `localhost` dengan port `8086`.

4. Buat database InfluxDB:
   ```bash
   influx
   CREATE DATABASE mqtt_data
   ```

---

## Instalasi dan Penggunaan

1. **Klon repositori ini:**
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. **Jalankan server MQTT:**
   ```bash
   python mqtt_server.py
   ```

3. Server akan mendengarkan di `0.0.0.0:1883` secara default:
   ```
   [LISTENING] Server is listening on 0.0.0.0:1883
   ```

---

## Gambaran Umum Kode

### Kelas `MQTTServer`
- **`__init__`**: Menginisialisasi server, klien InfluxDB, dan struktur data untuk klien serta topik.
- **`start()`**: Memulai server dan mendengarkan koneksi klien.
- **`handle_client()`**: Mengelola koneksi klien individu dan memproses paket MQTT.
- **`parse_packet_type()`**: Mendekode tipe paket dari data yang diterima.
- **`handle_connect()`**: Memproses paket `CONNECT` dan mengirim respons `CONNACK`.
- **`handle_publish()`**: Memproses paket `PUBLISH`, menyimpan data di InfluxDB, dan mengirim pesan ke subscriber.
- **`handle_subscribe()`**: Mengelola langganan klien ke topik.
- **`publish_to_subscribers()`**: Mengirim pesan ke klien yang berlangganan topik tertentu.
- **`create_publish_packet()`**: Membangun paket `PUBLISH` MQTT.
- **`handle_pingreq()`**: Menanggapi paket `PINGREQ`.
- **`handle_disconnect()`**: Menangani pemutusan klien dan membersihkan sumber daya.

---

## Contoh Alur Kerja

1. Seorang klien mengirim paket `CONNECT` ke server.
2. Setelah koneksi berhasil, klien berlangganan topik.
3. Klien lain mempublikasikan pesan ke topik yang dilanggan.
4. Pesan disimpan di **InfluxDB** dan diteruskan ke subscriber.

---

## Penanganan Kesalahan

- Paket tidak valid dicatat dengan `[ERROR]`.
- Tipe paket tidak dikenal dicatat dengan `[UNKNOWN PACKET TYPE]`.
- Pemutusan klien ditangani dengan baik untuk mengosongkan sumber daya.

---

## Ketergantungan

- **Python 3.x**
- **Klien InfluxDB Python**:  
  Instal melalui:
  ```bash
  pip install influxdb
  ```

---

## TODO

- **Integrasi Node-Red**: Memungkinkan manajemen alur kerja IoT yang mulus melalui **Node-Red**.
- **Penambahan Algoritma LSTM**: Integrasi **Long Short-Term Memory (LSTM)** untuk memprediksi penggunaan sumber daya dan menyesuaikan sumber daya sistem berdasarkan pola data yang masuk.

---

## Kontribusi

Silakan buka isu atau kirim pull request untuk meningkatkan server MQTT ini!

---

## Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT. Lihat file `LICENSE` untuk informasi lebih lanjut.

---

## Kontak

Untuk pertanyaan atau masalah, silakan hubungi pemelihara proyek ini.

---

Selamat menggunakan server MQTT! 🚀
