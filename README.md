# SatwikSetu - Agricultural Advisory AI Platform 🌾🤖

An intelligent microservices platform that empowers farmers with AI-driven insights for crop health, irrigation optimization, market pricing, and real-time notifications.

---

## 🌱 What You Can Do

**🩺 Disease Detection** - Upload crop images to instantly identify diseases using deep learning (PyTorch, CNN)

**💡 AI Advisory** - Get personalized treatment & prevention recommendations using RAG with LangChain & OpenAI

**💧 Smart Irrigation** - Receive data-driven irrigation schedules based on crop stage, soil moisture & weather

**📊 Market Prices** - Track real-time crop prices across mandis (markets) to maximize selling value

**🔔 Smart Alerts** - Get multi-channel notifications (Email, SMS, In-App) for diseases, advisories & price changes

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Nginx Load Balancer (Port 80)            │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌─────▼─────┐         ┌───▼─────┐
   │ Gateway │          │ PostgreSQL │         │  Redis  │
   │ (8000)  │          │ (Database) │         │ (Cache) │
   └────┬────┘          └────────────┘         └─────────┘
        │
        ├──────────┬──────────┬──────────┬──────────┐
        │          │          │          │          │
   ┌────▼──┐  ┌────▼──┐ ┌────▼──┐ ┌────▼──┐ ┌─────▼────┐
   │Disease│  │ AI    │ │Irriga-│ │Market │ │Notif-    │
   │Detect │  │Advisor│ │tion   │ │Price  │ │ication   │
   │ 8001 │  │ 8002 │ │ 8003 │ │ 8004 │ │ 8005    │
   └───────┘  └───┬───┘ └───────┘ └───────┘ └─────┬────┘
                  │                               │
              ┌───▼────────────────────────────────▼──┐
              │      Kafka Message Broker (9092)      │
              └───────────────────────────────────────┘
                  │
              ┌───▼──────┐
              │ Qdrant    │
              │(Vector DB)│
              │ (6333)    │
              └───────────┘
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **API Framework** | FastAPI, Uvicorn, Pydantic |
| **Backend** | Python 3.11+ |
| **Async/HTTP** | asyncpg, httpx, aiokafka |
| **AI/ML** | LangChain, OpenAI, PyTorch, TorchVision |
| **Vector Search** | Qdrant, Sentence Transformers |
| **Data Processing** | SQLAlchemy ORM, Alembic (migrations) |
| **Messaging** | Kafka, aiokafka |
| **Image Processing** | Pillow, NumPy, scikit-image |
| **Authentication** | JWT, fastapi-users |
| **Containerization** | Docker, Docker Compose |
| **Load Balancing** | Nginx |
| **Notifications** | Email (SMTP), SMS integrations |
---

## 🗄️ Databases Used

| Database | Purpose | Containerized |
|----------|---------|---|
| **PostgreSQL** | Main relational database for users, farms, uploads, advisories, market prices, irrigation logs, notifications | Yes (Port 5432) |
| **Redis** | In-memory cache for advisory results, price data, session storage | Yes (Port 6379) |
| **Qdrant** | Vector database for RAG knowledge base (disease advisories, treatment embeddings) | Yes (Port 6333) |
| **Kafka** | Message broker for async event streaming between services | Yes (Port 9092) |

---

## 🚀 Quick Start

### Prerequisites
- Docker v20.10+
- Docker Compose v2.0+
- Python 3.11+ (for local development)

### 1. Setup

```bash
# Clone and navigate
cd d:\Projects\SatwikSetu_APP

# Copy and configure environment
copy .env.example .env
# Edit .env with your settings (JWT_SECRET_KEY, OPENAI_API_KEY, etc.)
```

### 2. Start All Services

```bash
# Build and start containers
docker compose up -d

# Check service health
docker compose ps

# View logs
docker compose logs -f gateway
```

### 3. Initialize Database

```bash
# Run migrations
docker exec -it sf-gateway sh -c "cd /app && alembic upgrade head"

# Verify tables created
docker exec sf-postgres psql -U agentchiguru -d agentchiguru_db -c "\dt"
```

### 4. Access APIs

```
Main Gateway:         http://localhost:8000
Swagger Docs:         http://localhost:8000/docs
Health Check:         http://localhost:8000/health
Nginx Proxy:          http://localhost:80

Service Endpoints:
- Disease Detection:  http://localhost:8001
- AI Advisory:        http://localhost:8002
- Irrigation:         http://localhost:8003
- Market Price:       http://localhost:8004
- Notification:       http://localhost:8005
```


---

## 📂 Service Breakdown

**Gateway (8000)** - Main API entry point, JWT auth, request routing

**Disease Detection (8001)** - ML model inference (PyTorch/CNN/MobileNet), image upload handling

**AI Advisory (8002)** - RAG pipeline, vector search in Qdrant, LLM integration

**Irrigation (8003)** - Rule engine for irrigation recommendations

**Market Price (8004)** - Price aggregation, trend analysis, database queries

**Notification (8005)** - Event subscribers, multi-channel dispatcher (Email/SMS/In-app)

---

## 🔧 Environment Variables

```bash
DATABASE_URL=postgresql://user:password@postgres:5432/agentchiguru_db
JWT_SECRET_KEY=your-secret-key-here
LLM_PROVIDER=mock|openai|ollama
OPENAI_API_KEY=your-api-key
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
REDIS_URL=redis://redis:6379/0
QDRANT_HOST=qdrant
QDRANT_PORT=6333
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## 📞 Support

For issues or contributions, create a GitHub issue or contact the development team.
