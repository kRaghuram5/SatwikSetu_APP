# SatwikSetu - Agricultural Advisory AI Platform 🌾🤖

A comprehensive microservices-based platform for intelligent agricultural advisory, disease detection, irrigation management, and market price tracking.

---

## 🛠️ Tools & Technologies Stack

| Category | Tools |
|----------|-------|
| **Backend Framework** | FastAPI, Uvicorn |
| **Database** | PostgreSQL, SQLAlchemy ORM, Alembic (Migrations) |
| **Caching & Memory** | Redis |
| **Message Queue** | Kafka, aiokafka |
| **AI/ML & RAG** | LangChain, OpenAI, Sentence Transformers, Qdrant (Vector DB) |
| **Computer Vision** | PyTorch, TorchVision, Pillow, NumPy |
| **Data Validation** | Pydantic |
| **Async & HTTP** | asyncpg, httpx |
| **Authentication** | fastapi-users, JWT |
| **Containerization** | Docker, Docker Compose |
| **Reverse Proxy & Load Balancing** | Nginx |
| **Multi-Channel Notifications** | Email, SMS integrations |

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Services](#services)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

**SatwikSetu** is built on a **microservices architecture** with the following components:

```
┌─────────────────────────────────────────────────────────────┐
│                       Nginx Reverse Proxy (Port 80)         │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌───▼─────┐
   │ Gateway │          │ Database │          │  Cache  │
   │ (8000)  │          │(Postgres)│          │ (Redis) │
   └────┬────┘          └──────────┘          └─────────┘
        │
        ├─────────────────────┬─────────────────────┐
        │                     │                     │
   ┌────▼──────┐        ┌────▼─────┐         ┌──────▼────┐
   │   Disease │        │ Irrigation│         │  Market   │
   │ Detection │        │ Service   │         │   Price   │
   │  (8001)   │        │  (8003)   │         │  (8004)   │
   └───────────┘        └───────────┘         └───────────┘
        │                     │
        └─────────────┬───────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────▼────┐  ┌────▼───┐   ┌────▼──────┐
   │ AI Integ│  │ Kafka  │   │Notification
   │ Advisory│  │ Broker │   │ (8005)     │
   │ (8002)  │  │(9092)  │   └────────────┘
   └─────────┘  └────────┘
        │
   ┌────▼────┐
   │ Qdrant  │
   │(6333)   │
   └─────────┘
```

**Key Features:**
- 🔄 **Event-Driven Architecture**: Kafka for asynchronous workflows
- 🗄️ **Centralized Database**: PostgreSQL with SQLAlchemy ORM
- ⚡ **Caching Layer**: Redis for performance optimization
- 🔍 **Vector Search**: Qdrant for RAG-based advisory
- 🔐 **Authentication**: JWT-based security
- 📊 **Scalable**: Microservices can scale independently

---

## 🚀 Services

| Service | Port | Purpose |
|---------|------|---------|
| **Gateway** | 8000 | API entry point, request routing |
| **Disease Detection** | 8001 | ML-based disease identification from images |
| **AI Advisory** | 8002 | RAG pipeline for personalized recommendations |
| **Irrigation** | 8003 | Smart irrigation scheduling |
| **Market Price** | 8004 | Crop pricing and market trends |
| **Notification** | 8005 | Multi-channel alerts (Email, SMS, In-App) |
| **Nginx** | 80 | Reverse proxy and load balancing |

---

## 📦 Prerequisites

- **Docker**: v20.10+
- **Docker Compose**: v2.0+
- **Python**: 3.11+ (for local development)
- **Git**

---

## 🏃 Quick Start

### 1. Clone & Setup

```bash
# Navigate to project directory
cd d:\workspace\SatwikSetu_APP

# Copy environment configuration
copy .env.example .env

# Update .env with your settings (JWT key, LLM API keys, etc.)
```

### 2. Start Services

```bash
# Build and start all services
docker compose up -d

# View logs
docker compose logs -f gateway

# Check service health
docker compose ps
```

### 3. Initialize Database

```bash
# Run database migrations
docker exec -it sf-gateway sh -c "cd /app && alembic upgrade head"

# Verify database tables created
docker exec sf-postgres psql -U agentchiguru -d agentchiguru_db -c "\dt"
```

### 4. Access APIs

```
Gateway/Main API:     http://localhost:8000
API Documentation:    http://localhost:8000/docs
Gateway Health:       http://localhost:8000/health

Nginx Proxy:          http://localhost (Port 80)

Individual Services:
- Disease Detection:  http://localhost:8001
- AI Advisory:        http://localhost:8002
- Irrigation:         http://localhost:8003
- Market Price:       http://localhost:8004
- Notification:       http://localhost:8005
```

---

## 📁 Project Structure

```
SatwikSetu_APP/
├── shared/                      # Shared code across all services
│   ├── config.py               # Global settings
│   ├── database.py             # SQLAlchemy setup
│   ├── models/                 # ORM models (User, Farm, Upload, etc.)
│   │   ├── user.py
│   │   ├── farm.py
│   │   ├── upload.py
│   │   ├── advisory.py
│   │   ├── irrigation.py
│   │   ├── market_price.py
│   │   └── notification.py
│   └── schemas/
│       └── events.py           # Kafka event schemas
│
├── migrations/                  # Alembic database migrations
│   ├── env.py
│   ├── versions/
│   │   └── 001_initial_schema.py
│   └── script.py.mako
│
├── gateway/                     # API Gateway Service (Port 8000)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── config.py
│       └── routes/              # API endpoint handlers
│           ├── disease.py
│           ├── advisory.py
│           ├── irrigation.py
│           ├── market.py
│           └── notification.py
│
├── disease_detection/           # Disease Detection Service (Port 8001)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       └── [ML model code]
│
├── ai_advisory/                 # AI Advisory Service (Port 8002)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       └── [RAG implementation]
│
├── irrigation/                  # Irrigation Service (Port 8003)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       └── main.py
│
├── market_price/                # Market Price Service (Port 8004)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       └── main.py
│
├── notification/                # Notification Service (Port 8005)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       └── main.py
│
├── nginx/
│   └── nginx.conf              # Reverse proxy configuration
│
├── docker-compose.yml          # Service orchestration
├── alembic.ini                 # Alembic configuration
├── .env                        # Environment variables
├── .env.example                # Example environment file
└── README.md                   # This file
```

---

## 🔌 API Endpoints

### Gateway (Main API)

```
GET  /health                              # Health check
GET  /docs                                # Swagger API documentation

# Disease Detection Routes
POST /api/v1/disease/detect               # Analyze image for disease
GET  /api/v1/disease/uploads/{upload_id}  # Get detection results

# AI Advisory Routes
GET  /api/v1/advisory/{upload_id}         # Get advisory for disease
GET  /api/v1/advisory/search              # Search advisories

# Irrigation Routes
GET  /api/v1/irrigation/recommend         # Get irrigation recommendation
GET  /api/v1/irrigation/history/{farm_id} # Get irrigation history

# Market Price Routes
GET  /api/v1/market-prices                # Get current prices
GET  /api/v1/market-prices/trends/{crop}  # Get price trends

# Notification Routes
GET  /api/v1/notifications/{farmer_id}    # List notifications
POST /api/v1/notifications/{id}/mark-read # Mark as read
DELETE /api/v1/notifications/{id}         # Delete notification
```

### Example Requests

```bash
# 1. Upload image for disease detection
curl -X POST "http://localhost:8000/api/v1/disease/detect" \
  -F "image=@path/to/image.jpg" \
  -F "crop=tomato" \
  -F "farmer_id=123e4567-e89b-12d3-a456-426614174001" \
  -F "farm_id=223e4567-e89b-12d3-a456-426614174002"

# 2. Get irrigation recommendation
curl -X GET "http://localhost:8000/api/v1/irrigation/recommend?crop=rice&soil_moisture=45&temperature=28&growth_stage=vegetative"

# 3. Get market prices
curl -X GET "http://localhost:8000/api/v1/market-prices?crop=rice&state=Punjab"

# 4. Get notifications
curl -X GET "http://localhost:8000/api/v1/notifications/123e4567-e89b-12d3-a456-426614174001"
```

---

## 📊 Database Schema

### Users Table
```yaml
id: UUID (Primary Key)
email: String (Unique)
hashed_password: String
name: String
phone: String
state: String
district: String
role: Enum (farmer | agent | admin)
is_active: Boolean
created_at: DateTime
updated_at: DateTime
```

### Farms Table
```yaml
id: UUID (Primary Key)
farmer_id: UUID (Foreign Key → users.id)
name: String
crop_type: String (rice, wheat, cotton, etc.)
area_hectares: Float
soil_type: String (clay, sandy, loamy)
location: String
```

### Uploads Table
```yaml
id: UUID (Primary Key)
farmer_id: UUID (FK)
farm_id: UUID (FK)
image_path: String
disease_detected: String
confidence: Float (0.0-1.0)
crop: String
uploaded_at: DateTime
processed_at: DateTime
```

### Advisories Table
```yaml
id: UUID (Primary Key)
upload_id: UUID (FK, Unique)
disease: String
crop: String
treatment: Text
organic_alternative: Text
prevention: JSON
fertilizer: String
pesticide: String
created_at: DateTime
```

### Irrigation Logs Table
```yaml
id: UUID (Primary Key)
farm_id: UUID (FK)
crop: String
growth_stage: Enum
soil_moisture: Float (%)
temperature: Float (°C)
water_qty_liters_per_hectare: Float
frequency_days: Float
recommended_at: DateTime
is_applied: DateTime (nullable)
```

### Market Prices Table
```yaml
id: UUID (Primary Key)
crop: String (indexed)
state: String (indexed)
mandi: String
price_per_quintal: Float
price_per_kg: Float
price_date: DateTime
fetched_at: DateTime
```

### Notifications Table
```yaml
id: UUID (Primary Key)
farmer_id: UUID (FK)
notification_type: Enum
channel: Enum (email | sms | in_app | push)
title: String
message: Text
status: Enum (pending | sent | failed | read)
created_at: DateTime
sent_at: DateTime
read_at: DateTime
```

---

## ⚙️ Configuration

### Environment Variables (.env)

Key variables to configure:

```bash
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/db_name

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_EXPIRATION_MINUTES=1440

# LLM Provider
LLM_PROVIDER=mock|openai|ollama
OPENAI_API_KEY=your-api-key

# Services
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
REDIS_URL=redis://redis:6379/0
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Building Custom Images

```bash
# Build individual service
docker compose build gateway

# Build all services
docker compose build

# Build with no cache
docker compose build --no-cache
```

---

## 👨‍💻 Development

### Local Development Setup

```bash
# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r gateway/requirements.txt

# Run migrations
alembic upgrade head

# Start gateway locally
cd gateway
uvicorn app.main:app --reload --port 8000
```

### Adding New Migration

```bash
# Auto-generate migration
docker exec -it sf-gateway sh -c "cd /app && alembic revision --autogenerate -m 'Add new column'"

# Apply migration
docker exec -it sf-gateway sh -c "cd /app && alembic upgrade head"

# Rollback migration
docker exec -it sf-gateway sh -c "cd /app && alembic downgrade -1"
```

### Database Operations

```bash
# Connect to database
docker exec -it sf-postgres psql -U agentchiguru -d agentchiguru_db

# Useful psql commands:
\dt                    # List tables
\d table_name          # Describe table
SELECT COUNT(*) FROM users;  # Count records
DROP DATABASE agentchiguru_db;  # Drop database
```

---

## 🐛 Troubleshooting

### Services Not Starting

```bash
# Check Docker logs
docker compose logs

# Check specific service
docker compose logs gateway

# Restart services
docker compose restart

# Stop and remove all containers
docker compose down
docker compose up -d
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker compose exec postgres pg_isready

# Verify DATABASE_URL in .env
docker compose exec gateway printenv | grep DATABASE_URL

# Rebuild gateway container
docker compose down gateway
docker compose up -d gateway
```

### Port Conflicts

```bash
# List ports in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# Change port in docker-compose.yml if needed
# Example: "8001:8000" maps host port 8001 to container port 8000
```

### Migrations Failed

```bash
# Check migration history
docker exec -it sf-gateway alembic current
docker exec -it sf-gateway alembic history

# Manual database reset (WARNING: deletes data!)
docker exec -it sf-postgres psql -U agentchiguru -d agentchiguru_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker compose exec gateway alembic upgrade head
```

### Kafka Issues

```bash
# Check Kafka topics
docker compose exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list

# Create topic manually
docker compose exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --create --topic disease.detected --partitions 3 --replication-factor 1
```

---

## 📞 Support & Contact

For issues, questions, or contributions:

- 📧 Email: support@satwiksetu.com
- 🐛 Bug Reports: Create GitHub issue
- 💬 Discussions: Use GitHub Discussions

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

Built as part of the Agricultural AI Bootcamp program.

References:
- FastAPI Documentation: https://fastapi.tiangolo.com
- PostgreSQL: https://www.postgresql.org
- Docker: https://www.docker.com
- Kafka: https://kafka.apache.org
- Qdrant: https://qdrant.tech

---

**Happy Farming! 🌾✨**
