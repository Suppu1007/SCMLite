SCMLite — Smart Supply Chain & Logistics Tracking System

SCMLite is an intelligent logistics management system that enables:

✔ Real-time shipment tracking using IoT + Kafka
✔ Secure role-based access authentication
✔ Live data streaming dashboard
✔ Email notifications for shipment creation & status updates
✔ Admin control panel for user & shipment management


🧩 Project Features

| Module              | Description                                   |
| ------------------- | --------------------------------------------- |
| Authentication      | Secure login, logout, signup with JWT cookies |
| Admin Dashboard     | Manage users, shipments, role changes         |
| Shipment Tracking   | Real-time IoT based status detection          |
| Kafka Integration   | Event-driven updates from IoT devices         |
| MongoDB Database    | Stores shipment + device data                 |
| Email Notifications | Gmail SMTP alerts to sender/receiver          |
| Responsive UI       | Clean Bootstrap-based interface               |

Project Structure

app/
 ├─ core/              # Config, security, dependencies
 ├─ db/                # (future use: DB migrations / indexes)
 ├─ routes/            # All FastAPI route endpoints
 ├─ services/          # Business logic (shipments, tracking, status)
 ├─ templates/         # UI pages (Jinja2)
 ├─ static/            # CSS/JS/Assets
 ├─ utils/             # Email, helper utilities
 ├─ main.py            # App entrypoint for FastAPI

consumer/
 ├─ consumer.py        
 ├─ Dockerfile

producer/
 ├─ producer.py        
 ├─ Dockerfile

 server/
 ├─ server.py        # Server data
 ├─ Dockerfile

docker-compose.yml     # Kafka + Apache kafka(krafka) stack




Architecture



 ┌────────────┐     JWT Cookies     ┌─────────────┐
 │   Client   │ ◀──────────────────▶│   FastAPI   │
 └─────▲──────┘                     └─────▲───────┘
       │ HTML Pages & Live Data           │
       │                                   │ REST + Kafka Consumer
       ▼                                   ▼
 ┌──────────────┐                   ┌──────────────┐
 │  MongoDB     │◀─────────────▶│  Kafka Broker │
 │ Users,Shipmnt│                │ IoT Device Msg│
 └──────────────┘                └───────────────┘
                                             ▲
                                             │
                                IoT Sensor Stream (Route_To, Location, etc.)


Tech Stack

| Component         | Technology                   |
| ----------------- | ---------------------------- |
| Backend           | FastAPI (Python)             |
| Frontend          | Jinja2 Templates + Bootstrap |
| Database          | MongoDB                      |
| Message Streaming | Apache Kafka                 |
| Auth              | JWT + Cookies                |
| Email Service     | Gmail SMTP                   |
| Server            | Uvicorn / Gunicorn           |


