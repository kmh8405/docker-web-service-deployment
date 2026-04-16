# Docker Web Service Deployment

Docker를 활용하여 FastAPI와 MySQL 기반의 웹 서비스를 컨테이너 환경에서 구성하고 배포 과정을 학습하는 프로젝트입니다.

---

## 🏗️ Architecture

* API Server: FastAPI
* Database: MySQL
* Inference Worker: LLM (llama.cpp)
* Container Management: Docker Compose

---

## 🚀 Features

### Day 1

* Built a FastAPI-based API server
* Configured a MySQL database container
* Created a custom Docker image using Dockerfile
* Orchestrated multiple containers using Docker Compose

---

### Day 2

* Integrated MySQL with FastAPI using SQLAlchemy
* Separated API and Worker services for better architecture
* Introduced LLM inference worker using `llama-cpp-python`
* Structured the project for handling concurrency issues
* Managed multiple services (api, db, worker) with Docker Compose

---

## 📁 Project Structure

```
docker/
├── api/
│   ├── main.py
│   ├── connection.py
│   ├── Dockerfile
│   ├── requirements.txt
│
├── worker/
│   ├── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── models/
│   ├── .dockerignore
│
├── docker-compose.yml
├── .env
├── .gitignore
├── README.md
```

---

## 🛠️ How to Run

```bash
docker compose up -d --build
```

* First run requires build
* After that:

```bash
docker compose up -d
```

* Stop all containers:

```bash
docker compose down
```

---

## 🌐 API Endpoint

* Health Check
  http://localhost:8000/health-check

---

## 🗄️ Database

* Host: 127.0.0.1
* Port: 33061
* User: root
* Password: defined in `.env`

---

## ⚠️ Common Issues

### 1. Port already in use

```
bind: address already in use
```

**Cause**

* The specified port is already being used by another container or process

**Solutions**

* Stop existing containers (`docker compose down`)
* Change the port number (e.g., 33061)
* Remove port mapping if it is not required

---

### 2. MySQL connection refused (OperationalError)

```
sqlalchemy.exc.OperationalError:
Can't connect to MySQL server on 'db'
```

**Cause**

* API attempts to connect before MySQL is fully initialized
* Docker Compose starts containers in parallel

**Solutions**

1. Restart containers

```
docker compose down
docker compose up -d
```

2. Start DB first

```
docker compose up db -d
# wait a few seconds
docker compose up api -d
```

3. Use healthcheck (recommended)

Ensure that the database is fully ready before the API starts.

```
db:
  image: mysql:8.0
  environment:
    MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    MYSQL_DATABASE: ${MYSQL_DATABASE}
  ports:
    - "33061:3306"
  healthcheck:
    test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
    interval: 5s
    retries: 5

api:
  build: ./api
  ports:
    - "8000:8000"
  depends_on:
    db:
      condition: service_healthy
```

* `healthcheck` verifies that MySQL is actually ready to accept connections
* `depends_on.condition: service_healthy` ensures API starts **after DB is ready**
* This is the most reliable solution in multi-container environments

---

### 4. MySQL Workbench reconnect loop

**Symptom**

* Password prompt repeatedly appears

**Cause (likely)**

* DB container is not fully ready or unstable
* Continuous reconnection attempts from client

**Observation**

* Workbench connects after delay (manual timing)
* FastAPI connects immediately → failure occurs

**Solution**

* Ensure DB is fully initialized before API access
* Use volume to stabilize DB state

---

## 📌 Notes

* This project evolves from a single-container setup to a multi-container architecture
* API and Worker are separated to handle concurrency issues in model inference
* The `--reload` option is used in development for automatic server restart
* In Docker Compose, service names act as hostnames (e.g., `db`)
* `depends_on` does not guarantee that the database is ready to accept connections

### Docker & Build

* Code changes require rebuilding the image:

```bash
docker compose up -d --build
```

* `docker compose down` removes containers
* `docker compose up -d` restarts without rebuild

### Volume

* `./api:/app`
  → Local code is mounted into the container

* `local_db:/var/lib/mysql`
  → MySQL data is persisted

### Model Handling

* Model files (e.g., `.gguf`) are excluded from Docker build using `.dockerignore`
* Models are mounted via volume instead of being included in the image
* This reduces image size and speeds up build time

### Database Connection

* Use `db` as hostname inside Docker network (not `localhost`)
* API may attempt connection before DB is ready

### Error Types

* OperationalError
  → DB connection failure

* ProgrammingError
  → Query or schema issue

---
