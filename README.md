# Docker Web Service Deployment

Docker를 활용하여 FastAPI와 MySQL 기반의 웹 서비스를 컨테이너 환경에서 구성하고 배포 과정을 학습하는 프로젝트입니다.

---

## 🏗️ Architecture

* API Server: FastAPI
* Database: MySQL
* Inference Worker: LLM (llama.cpp)
* Message Broker: Redis (Queue + Pub/Sub)
* Container Management: Docker Compose

---

## 🚀 Features

### Day 1

* Built a FastAPI-based API server
* Configured a MySQL database container
* Created a custom Docker image using Dockerfile
* Orchestrated multiple containers using Docker Compose

### Day 2

* Integrated MySQL with FastAPI using SQLAlchemy
* Separated API and Worker services for better architecture
* Introduced LLM inference worker using llama-cpp-python
* Structured the project for handling concurrency issues

### Day 3

* Introduced Redis as a message broker
* Implemented Queue-based task distribution (LPUSH / BRPOP)
* Implemented Pub/Sub for real-time communication
* Built streaming chat endpoint using StreamingResponse
* Designed full pipeline:

  FastAPI → Redis Queue → Worker → Redis Pub/Sub → FastAPI → Client

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

```bash
docker compose up -d
```

* Restart without rebuild

```bash
docker compose down
```

* Stop all containers

---

## 🌐 API Endpoint

* Health Check
  http://localhost:8000/health-check

* Chat (Streaming)

  ```bash
  curl -N -X POST http://127.0.0.1:8000/chats \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Python이 뭐야?"}'
  ```

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

**Solutions**

* Stop containers (`docker compose down`)
* Change port
* Remove port mapping if unnecessary

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

### 3. Redis / API Internal Server Error

**Symptom**

* `Internal Server Error` occurs when calling `/chats`

**Cause**

* Typo in Redis Pub/Sub initialization

```python
pubusb()  ❌
pubsub()  ✅
```

---

### 4. Infinite loading (no response from /chats)

**Symptom**

* Request hangs with no response (infinite loading)

**Cause**

* Token parsing error in worker

```python
chunk["choices"]["0"]  ❌
chunk["choices"][0]    ✅
```

**Additional Check**

* Verify Redis queue status

```bash
docker exec -it docker-redis-1 redis-cli
LRANGE queue 0 -1
```

---

### 5. MySQL Workbench reconnect loop

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

* API and Worker are separated to prevent concurrency issues
* Redis is used for:
  * Queue (task distribution)
  * Pub/Sub (result delivery)
* LLM inference is handled by Worker to avoid race conditions
* Docker Compose service names act as internal hostnames (`db`, `redis`)
* Volume is used to persist MySQL data
* `--reload` is for development only (auto-restart on code change)

---
