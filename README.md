
# 📦 **SCMLite – Supply Chain Management System**

A full-stack SCM platform with FastAPI backend, Kafka streaming, MongoDB storage, role-based access, and responsive UI.

---

## 🚀 **1. Overview**

SCMLite provides shipment management, device live-stream data, admin role control, and secure authentication.
The system includes a FastAPI server, Kafka producer/consumer pipeline, and MongoDB database.

---

## ⭐ **2. Key Features**

* User authentication & JWT-based sessions
* Admin dashboard with role management
* Email notifications for role updates
* Create & track shipments
* Live device data streaming via Kafka
* Responsive UI using Bootstrap
* MongoDB persistence
* Dockerized microservice architecture

---

## 🏗️ **3. Architecture**

```
Socket Server → Kafka Producer → Kafka Broker → Kafka Consumer → MongoDB → FastAPI → UI
```

---

## 🧰 **4. Tech Stack**

* **Backend:** FastAPI, Python
* **Database:** MongoDB
* **Streaming:** Apache Kafka
* **UI:** Bootstrap + Jinja Templates
* **Containerization:** Docker + Docker Compose
* **Email:** Gmail SMTP

---

## 📁 **5. Folder Structure**

```
FullStack/
 ├── server/
 │   ├── app/
 │   │   ├── core/ (config, security, dependencies)
 │   │   ├── db/ (mongo connection)
 │   │   ├── routes/ (auth, admin, shipments, profile, streams)
 │   │   ├── utils/ (email, tokens, password helpers)
 │   │   ├── main.py
 │   ├── templates/ + static/
 │   ├── Dockerfile
 │   └── socket_server.py
 ├── producer/ (Kafka producer)
 ├── consumer/ (Kafka consumer)
 ├── kafka-init.sh
 ├── docker-compose.yml
 └── .env
```

