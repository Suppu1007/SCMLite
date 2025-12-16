# SCMLite — Smart Supply Chain & Logistics Tracking System

SCMLite is a scalable, secure, and real-time logistics management platform designed to improve shipment visibility and supply chain reliability.
It leverages an event-driven microservices architecture with Apache Kafka to enable asynchronous updates, real-time insights, and fault-tolerant operations.

Built using **FastAPI, Kafka, MongoDB, and Docker**, SCMLite is suitable for both **academic learning** and **real-world enterprise deployment**.

---

## Problem Statement

Traditional supply chain and logistics systems face several challenges:

* Delayed shipment visibility
* Manual and synchronous update processing
* Limited real-time analytics
* Monolithic and tightly coupled system design

These limitations result in poor scalability, reduced reliability, and delayed decision-making.

---

## Proposed Solution

SCMLite addresses these challenges by:

* Streaming real-time shipment lifecycle events using Apache Kafka
* Decoupling services through event-driven communication
* Providing secure authentication and role-based access control
* Containerizing all services for consistent and scalable deployment

---

## Key Features

### Authentication & Security

* User and Admin roles
* JWT-based API authentication
* Cookie-based authentication for UI
* Middleware-based route protection

### Shipment Lifecycle Management

* Shipment creation, updates, and tracking
* Shipment status history and movement logs
* Email notifications for key shipment events

### Event Streaming with Kafka

* Shipment updates published as Kafka events
* Independent consumer service for asynchronous processing
* Fault isolation and high system resilience

### Admin Dashboard

* User and role management
* Shipment monitoring
* Stream-based real-time operational view

### User Interface

* Server-side rendered UI using Jinja2
* Responsive design with Bootstrap
* Simple and intuitive business workflow

---

## System Architecture

```
┌─────────────────────────────┐
│ Web UI (Jinja2 + JavaScript)│
│ Cookie-based Authentication │
└───────────────┬─────────────┘
                │
                ▼
      ┌────────────────────────┐
      │ FastAPI Backend         │
      │ Auth | Shipments | Admin│
      └────────────┬───────────┘
                   │
              JWT-secured APIs
                   │
                   ▼
┌────────────────┐   Kafka Stream   ┌────────────────┐
│ Producer        │────────────────►│ Kafka Broker    │
│ Event Publisher │                 │ Topics          │
└────────────────┘                 └────────┬────────┘
                                             │
                                             ▼
                                  ┌────────────────────┐
                                  │ Consumer Service    │
                                  │ DB Update + Email   │
                                  └──────────┬─────────┘
                                             │
                                             ▼
                                      MongoDB Database
```

### Architectural Benefits

* Loose coupling between services
* High fault tolerance
* Horizontal scalability
* Real-time event processing

---

## Project Structure

```
SCMLite/
│
├── app/
│   ├── core/                 # Configuration, JWT, security
│   ├── routes/               # API and UI route handlers
│   ├── templates/            # HTML templates
│   ├── static/               # CSS and JavaScript files
│   └── main.py               # FastAPI application entry point
│
├── producer/                 # Kafka event producer service
│   └── producer.py
│
├── consumer/                 # Kafka event consumer service
│   └── consumer.py
│
├── docker-compose.yml        # Multi-service orchestration
├── Dockerfile.app            # FastAPI application Dockerfile
└── README.md                 # Project documentation
```

---

## Technology Stack

| Layer             | Technology             |
| ----------------- | ---------------------- |
| Backend Framework | FastAPI                |
| Frontend          | Jinja2, Bootstrap      |
| Event Streaming   | Apache Kafka           |
| Database          | MongoDB                |
| Authentication    | JWT, Cookies           |
| Containerization  | Docker, Docker Compose |

---

## Docker Setup & Execution

### Start All Services

```bash
docker compose up --build -d
```

### Stop All Services

```bash
docker compose down
```

### View Logs

```bash
docker logs app -f
docker logs producer -f
docker logs consumer -f
```

### Rebuild Only the Application Service

```bash
docker compose up -d --build app
```

---

## Learning Outcomes and Academic Relevance

| Concept                          | Covered |
| -------------------------------- | ------- |
| Microservices Architecture       | Yes     |
| REST API Development             | Yes     |
| JWT-based Authentication         | Yes     |
| Cookie-based UI Security         | Yes     |
| Kafka Producer–Consumer Pattern  | Yes     |
| Asynchronous Processing          | Yes     |
| Email Automation                 | Yes     |
| Docker & Container Orchestration | Yes     |
| Distributed Systems Design       | Yes     |

This project is highly suitable for:

* Cloud Computing coursework
* Distributed Systems labs
* DevOps and Microservices learning
* Final year or capstone academic projects

---

## Future Enhancements

* Real-time UI updates using WebSockets
* GPS-based shipment tracking with IoT integration
* Kafka dead-letter queues and retry mechanisms
* Advanced analytics dashboard
* Fine-grained RBAC permissions
* Monitoring using Prometheus and Grafana
* SMS and WhatsApp notification integration

---

## Conclusion

SCMLite demonstrates how modern logistics platforms can be designed using:

* Event-driven microservices
* Real-time data streaming
* Secure authentication mechanisms
* Containerized, cloud-ready deployments

The system aligns with enterprise-grade architecture principles while remaining accessible for academic exploration and learning.

