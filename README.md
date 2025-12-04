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



Architecture



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


