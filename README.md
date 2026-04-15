# Docker Web Service Deployment

Docker를 활용하여 FastAPI와 MySQL 기반의 웹 서비스를 컨테이너 환경에서 구성하고 배포 과정을 학습하는 프로젝트입니다.

---

## 🏗️ Architecture

- API Server: FastAPI
- Database: MySQL
- Container Management: Docker Compose

---

## 🚀 Features

### Day 1

- Built a FastAPI-based API server
- Configured a MySQL database container
- Created a custom Docker image using Dockerfile
- Orchestrated multiple containers using Docker Compose

---

## 📁 Project Structure
docker/
├── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── README.md
└── .env


---

## 🛠️ How to Run

```bash
docker compose up -d --build
```

---

## 🌐 API Endpoint

- Health Check:
    http://localhost:8000/health-check

---

## 🗄️ Database

- Host: 127.0.0.1
- Port: 33061
- User: root
- Password: (defined in .env)

---

## ⚠️ Common Issues

### 1. Port already in use

```bash
bind: address already in use
```

**Cause**
- The specified port is already being used by another container or process

**Solutions**
- Stop existing containers (`docker compose down`)
- Change the port number (e.g., 33061)
- Remove port mapping if it is not required

---

## 📌 Notes

- This is a basic setup for learning Docker-based web service deployment.
- The project will be extended in future sessions.
- The `--reload` option is used in development to automatically restart the server when code changes
- In Docker Compose, service names act as hostnames within the internal network
- `depends_on` only ensures container startup order, not service readiness

---