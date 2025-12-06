
# 🚚 SCMLite — Smart Supply Chain & Logistics Tracking System

SCMLite is a scalable, secure, and real-time logistics management platform designed to improve shipment visibility and supply chain reliability.  
It integrates modern microservice architecture with Kafka streaming to enable asynchronous updates, real-time insights, and fault-tolerant operations.

> Built with FastAPI, Kafka, MongoDB & Docker — Optimized for distributed systems learning and real-world enterprise deployment.

---

## 🎯 Problem Statement

Traditional supply chains struggle with:
- Delayed shipment visibility
- Manual update processing
- Lack of real-time tracking analytics
- Centralized tightly coupled architecture

SCMLite solves this by:
✔ Streaming real-time shipment events  
✔ Ensuring data consistency through event-driven processing  
✔ Implementing secure, role-based access  
✔ Containerizing services for elastic deployment  

---

## ✨ Key Features

### 🔐 Secure Login System
- User + Admin roles
- JWT for API security
- Cookies for UI authentication
- Route access control middleware

### 📦 Shipment Lifecycle Management
- Create, update & track shipments
- Movement history and status logs
- Email alerts for major updates

### ⚡ Event Streaming via Kafka
- Producer triggers shipment events
- Consumer processes updates asynchronously
- Fault-isolated microservices

### 🧑‍💼 Admin Dashboard
- Manage users, roles, shipments
- Real-time stream views

### 🖥 Clean and Responsive UI
- Jinja Templates + Bootstrap
- Simple UX for business operations

---

## 🏛️ Architecture Overview

```

```
            ┌───────────────────────────┐
            │     Web UI (Jinja + JS)   │
            │ Cookie Authentication     │
            └───────────────┬──────────┘
                            │
                            ▼
                ┌──────────────────────┐
                │ FastAPI Backend      │
                │ Auth / Shipments /   │
                │ Tracking / Admin     │
                └─────────┬────────────┘
                          │
                   APIs (JWT)
                          │
                          ▼
    ┌──────────────┐  Kafka Stream  ┌────────────────┐
    │ Producer      │──────────────►│ Kafka Broker    │
    │ Event Publish │               │ Topic Exchange  │
    └──────────────┘               └───────┬────────┘
                                           │
                                           ▼
                               ┌──────────────────────┐
                               │ Consumer Service     │
                               │ DB Update + Email    │
                               └─────────┬────────────┘
                                         │
                                         ▼
                                  MongoDB Database
```

```

📌 Benefits: Loose coupling │ Resilience │ Scale-out capacity │ Real-time  

---

## 📂 Project Structure

```

.
├── app/
│   ├── core/            # Config + JWT Security
│   ├── routes/          # UI + API Routers
│   ├── templates/       # HTML Pages
│   ├── static/          # CSS, JS
│   └── main.py          # App Entry Point
├── producer/            # Kafka Event Producer
├── consumer/            # Kafka Event Consumer
├── docker-compose.yml   # Service Orchestration
├── Dockerfile.app       # Build Script for FastAPI App
└── README.md

````

---

## 🧰 Tech Stack

| Layer | Technology |
|------|------------|
| Framework | FastAPI |
| UI / Frontend | Jinja2 + Bootstrap |
| Streaming | Apache Kafka |
| Database | MongoDB |
| Authentication | JWT + Cookies |
| Deployment | Docker, Docker Compose |

---

## 🐳 Docker Usage (Main Commands)

### ▶ Start All Services
```bash
docker compose up --build -d
````

### ⛔ Stop Everything

```bash
docker compose down
```

### 🔍 View Logs

```bash
docker logs app -f
docker logs consumer -f
docker logs producer -f
```

### ♻ Rebuild App Service

```bash
docker compose up -d --build app
```

---

## 🧠 Learning Outcomes (Academic Value)

| Concept                            | Covered |
| ---------------------------------- | ------- |
| Microservices Architecture         | ✔       |
| JWT API Security                   | ✔       |
| Cookie-based UI Auth               | ✔       |
| Kafka Producer–Consumer Event Flow | ✔       |
| Email automation                   | ✔       |
| Container orchestration            | ✔       |
| Real-world deployment workflow     | ✔       |

🎓 *Strong academic applicability for Cloud Computing / DevOps / Distributed Systems*

---

## 🔮 Future Enhancements

* Real-time UI updates via WebSockets
* GPS tracking using IoT sensors
* Kafka DLQ & message retries
* Advanced admin analytics dashboard
* RBAC with granular permissions
* Monitoring using Prometheus + Grafana
* Alerts via SMS / WhatsApp API

---

## 🧾 Conclusion

SCMLite demonstrates how modern logistics systems can:
✨ Scale using microservices
✨ Stream events reliably
✨ Ensure secure and seamless operations
✨ Deploy consistently across environments using Docker

> This project showcases a real-world, industry-relevant supply chain system aligned with enterprise architecture standards.

---

## 📜 MIT License

```
MIT License

Copyright (c) 2025 Suppu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

