

SCMLite

This project implements a **real-time IoT data streaming architecture** using:

* **Socket Server** → generates live telemetry
* **Kafka Producer** → receives socket data & pushes to Kafka
* **Kafka Consumer** → reads Kafka topic & stores data in **MongoDB**
* **MongoDB** → persistent storage for streamed device logs

This README covers ONLY these folders:

```
server/
producer/
consumer/
```

---

## 📂 Folder Overview

### **server/**

Contains the complete data-generation and optional web layer.

| File/Folder               | Description                                    |
| ------------------------- | ---------------------------------------------- |
| `socket_server.py`        | TCP server that generates IoT device JSON data |
| `app.py`                  | Optional web layer / API / dashboard           |
| `static/`                 | CSS, JS, images for UI                         |
| `templates/`              | HTML templates                                 |
| `Dockerfile.socket`       | Dockerfile for socket server                   |
| `Dockerfile`              | Dockerfile for server web app                  |
| `requirements_socket.txt` | Dependencies for socket server                 |
| `requirements.txt`        | Dependencies for server web app                |

---

### **producer/**

Reads data from the socket server → publishes to Kafka.

| File               | Description                                                         |
| ------------------ | ------------------------------------------------------------------- |
| `producer.py`      | Connects to socket → sends messages to Kafka topic `device_streams` |
| `Dockerfile`       | Builds producer container                                           |
| `requirements.txt` | Kafka dependencies (`kafka-python`)                                 |

---

### **consumer/**

Reads Kafka messages → stores them in **MongoDB**.

| File               | Description                                                    |
| ------------------ | -------------------------------------------------------------- |
| `consumer.py`      | Subscribes to Kafka → inserts messages into MongoDB collection |
| `Dockerfile`       | Builds consumer container                                      |
| `requirements.txt` | Kafka + MongoDB dependencies                                   |

---

# ⚙️ System Architecture

```
    [server/socket_server.py]
               ↓ TCP (5050)
     [producer/producer.py]
               ↓ Kafka Topic (device_streams)
      [Kafka Broker + Zookeeper]
               ↓
      [consumer/consumer.py]
               ↓
           [MongoDB]
```

---

# 📌 MongoDB Usage

The consumer stores each incoming device packet into a MongoDB collection.

Example document stored:

```json
{
  "Device_ID": 1156,
  "Battery_Level": 3.85,
  "Temperature": 27.1,
  "Route_From": "Chennai, India",
  "Route_To": "London, UK",
  "Timestamp": "2025-11-14 17:27:36"
}
```

# 🧪 Running the Pipeline 

## **1️⃣ Start MongoDB, Kafka & Zookeeper**

Using Docker Compose (root-level `docker-compose.yml`):

```bash
docker compose up --build
```

Starts:

* Zookeeper
* Kafka broker
* MongoDB
* Producer
* Consumer
* Socket server

---

## **2️⃣ View Logs**

Socket server:

```bash
docker logs -f socket-server
```

Producer:

```bash
docker logs -f producer
```

Consumer:

```bash
docker logs -f consumer
```

---

## **3️⃣ Verify MongoDB Storage**

Enter MongoDB shell:

```bash
docker exec -it mongo mongosh
use iot_stream
db.device_logs.find().pretty()
```

---

# ✔️ Summary

This repository provides a complete **real-time streaming stack**:

* Synthetic IoT data generator 
* Kafka producer → Kafka topic
* Kafka consumer → MongoDB insert
* Dockerized and modular
* Clean separation of server, producer, and consumer

