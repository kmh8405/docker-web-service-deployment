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

### Day 4

* Introduced async database handling using SQLAlchemy (aiomysql)
* Implemented Conversation & Message data model (1:N relationship)
* Built conversation-based chat system with persistent history
* Added APIs:
  * Create conversation
  * Retrieve messages
  * Send message with context
* Integrated full conversation context into LLM inference
* Stored assistant responses in DB after streaming completes
* Improved worker robustness with JSON parsing error handling
* Refactored configuration using environment variables
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

  * Create Conversation

  ```bash
  POST /conversations
  ```

  * Get Messages

  ```bash
  GET /conversations/{conversation_id}/messages
  ```

  * Send Message (Streaming)
  ```bash
  POST /conversations/{conversation_id}/messages
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

### 6. MySQL Access Denied (Docker Internal Network)

**Error**

`Access denied for user 'root'@'172.x.x.x'`

**Cause**

* Docker containers communicate via internal network (172.x.x.x)
* MySQL treats this as external access
* Root user not allowed for remote connections
* Additionally, API container did not have required environment variables

**Key Problem**

* `MYSQL_ROOT_PASSWORD` was not set inside API container
* DB authentication failed due to missing credentials

**Solution**

1. Add environment variables to API container

```yaml
api:
  environment:
    MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    MYSQL_DATABASE: ${MYSQL_DATABASE}
    MYSQL_HOST: ${MYSQL_HOST}
    MYSQL_PORT: ${MYSQL_PORT}
```

2. Rebuild containers

```bash
docker compose down -v
docker compose up -d --build
```

3. Verify environment variables

```bash
docker exec -it docker-api-1 bash
echo $MYSQL_ROOT_PASSWORD
```

4. Run table creation again

```python
from models import Base
from connection import engine
Base.metadata.create_all(engine)
```

---

## 📌 Notes

* API and Worker are separated to avoid concurrency issues in LLM inference
* Redis is used for:
  * Queue → task delivery (FastAPI → Worker)
  * Pub/Sub → result streaming (Worker → FastAPI)
* LLM runs only in Worker to prevent race conditions
* Conversation history is stored in MySQL and passed to the model as context
* Async DB (`aiomysql`) is used for non-blocking database operations
* Docker Compose service names act as internal hostnames (`db`, `redis`)
* Volume is used to persist MySQL data
* `--reload` is for development only



---
