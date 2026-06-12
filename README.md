# SenAI CRM Intelligence Platform

An autonomous CRM triage system that classifies, prioritizes, and acts on inbound emails using a multi-layer intelligence engine with RAG, LangGraph agents, and live web intelligence.

## Architecture

```
Frontend (React + Vite)
    │
    ▼
Backend (FastAPI)
    │
    ├── Ingestion Pipeline ──► PostgreSQL
    │
    ├── RAG Pipeline ───────► ChromaDB
    │
    ├── Classifier ─────────► Gemini LLM + Pydantic
    │
    ├── Planner ────────────► LangGraph
    │
    ├── Agent Executor ─────► Tools (RAG, Thread, Contact, Intel, Reply, Escalation)
    │
    └── Analytics ──────────► Recharts Dashboard
```

## Key Components

1. **Email Ingestion & Streaming Pipeline** - Handles duplicate `message_id`s, normalizes payloads, applies heuristic pre-filtering (spam, security, legal/GDPR keywords), and computes priority scores.
2. **Multi-Layer Intelligence Engine** - Combines RAG policy context, CRM contact profiles, thread history, and live web intelligence.
3. **RAG Knowledge Pipeline** - Chunks policy documents (300-500 tokens with overlap), embeds with HuggingFace, and stores in ChromaDB.
4. **Autonomous Triage Agent** - LangGraph workflow: `classify → plan → execute → finish` with full reasoning trace.
5. **Live Web Intelligence Module** - Scrapes public sentiment from G2 and Trustpilot with caching and fallback.
6. **Database Design** - SQLAlchemy ORM with Alembic migrations for `emails`, `contacts`, `threads`, `agent_runs`, `actions`, `audit_logs`, and `web_intelligence_cache`.
7. **Backend API** - FastAPI routers with structured error handling and CORS.
8. **Frontend Dashboard** - React SPA with Inbox, Agent Playground, Agent Runs, Analytics, and Thread Workspace.

## Safety-Critical Rules

The agent enforces hard safety guards:
- **Never auto-reply to spam, ransomware, legal threats, or GDPR requests**
- **Never auto-reply when urgency is Critical or `requires_human` is true**
- **All decisions include a reasoning trace for auditability**
- **Duplicate `message_id`s are handled idempotently**
- **Malformed payloads return structured validation errors**

## Quick Start with Docker

### Prerequisites

- Docker 24+
- Docker Compose 2+
- Google Gemini API key

### Environment Variables

Create `backend/.env`:
```env
DATABASE_URL=postgresql://senai:senai_password@db:5432/senai_crm
GEMINI_API_KEY=your_gemini_api_key
```

### Start All Services

```bash
docker-compose up --build
```

This starts:
- **Frontend** at `http://localhost:5173`
- **Backend API** at `http://localhost:8000`
- **ChromaDB** at `http://localhost:8001`
- **PostgreSQL** on port `5432`

### Seed the Knowledge Base

```bash
docker-compose exec backend python -m app.rag.seed
```

### Seed Sample Data

```bash
docker-compose exec backend python -m app.scripts.load_dataset
docker-compose exec backend python -m app.scripts.seed_contacts
```

### Run Email Simulation

```bash
docker-compose exec backend python -m app.api.stream
```

## Manual Setup (without Docker)

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Google Gemini API key

### Environment Variables

Create `backend/.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/senai_crm
GEMINI_API_KEY=your_gemini_api_key
```

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
```

### Seed the Knowledge Base

```bash
cd backend
python -m app.rag.seed
```

This loads all `.md` files from `backend/app/knowledge_base/` into ChromaDB.

### Seed Sample Data

```bash
cd backend
python -m app.scripts.load_dataset
python -m app.scripts.seed_contacts
```

### Run Email Simulation

```bash
cd backend
python -m app.api.stream
```

Or use the frontend Inbox page to trigger streaming via the `/api/stream/start` endpoint.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Running the Application

1. Start PostgreSQL and ensure the database exists
2. Start the backend: `cd backend && uvicorn app.main:app --reload`
3. Start the frontend: `cd frontend && npm run dev`
4. Open `http://localhost:5173`

## API Documentation

Interactive Swagger UI is available at `http://localhost:8000/docs` when the backend is running.

A static OpenAPI spec is also available at `http://localhost:8000/openapi.json`.

## Docker Configuration

### docker-compose.yml

```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: senai-frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - CHOKIDAR_USEPOLLING=true
      - NODE_ENV=development
    command: ["npm", "run", "dev"]
    networks:
      - senai-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: senai-backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      - chroma
    volumes:
      - ./backend:/app
    networks:
      - senai-network

  chroma:
    image: chromadb/chroma:latest
    container_name: senai-chroma
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma
    networks:
      - senai-network

volumes:
  chroma_data:

networks:
  senai-network:
    driver: bridge
```

### backend/Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000", "--reload"]
```

### frontend/Dockerfile

```dockerfile
FROM node:20

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
```

## Architecture Decisions and Trade-offs

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| FastAPI + SQLAlchemy | Type safety, async support, mature ecosystem | Slightly more boilerplate than raw SQL |
| LangGraph for agent workflow | Explicit state transitions, visualizable DAG | Learning curve vs simpler chains |
| ChromaDB for RAG | Local-first, no external service dependency | Less scalable than managed vector DBs |
| Gemini 2.5 Flash Lite | Cost-effective, fast inference | May need prompt tuning for edge cases |
| React + Vite frontend | Fast HMR, modern DX | Smaller ecosystem than Next.js |
| sessionStorage for agent results | Persists across tab navigation without backend state | Cleared on browser close |
| BeautifulSoup for web intel | No browser dependency, lightweight | May break if site HTML changes |
| Docker Compose | Single-command deployment, reproducible | Slightly higher resource usage |

## Known Limitations

- **RAG context is limited to top-k chunks**; very long policy documents may lose nuance.
- **Web intelligence scraping** depends on third-party site structure; may need maintenance if G2/Trustpilot change their HTML.
- **Thread grouping in Inbox** is client-side only; large datasets should be paginated server-side.
- **Performance benchmarks** are basic; production would need load testing with realistic traffic.
- **Special scenario handling** uses keyword matching; production should use LLM-based intent classification.
- **No multi-tenancy**; all data is in a single database schema.

## Knowledge Base

The `backend/app/knowledge_base/` folder contains policy documents used for RAG:
- `api_docs.md` - API documentation and rate limits
- `compliance_faq.md` - GDPR, security, and legal compliance rules
- `escalation_matrix.md` - Routing rules for different issue types
- `pricing_policy.md` - Plan pricing and upgrade/downgrade rules
- `refund_policy.md` - Refund eligibility and churn retention playbook
- `sla_policy.md` - Service level agreements and response times

**Yes, you should re-seed the RAG after modifying these files.** Run:
```bash
cd backend
python -m app.rag.seed
```

This will clear the existing ChromaDB collection and re-embed all updated documents.

## Project Structure

```
backend/
  app/
    agent/          - LangGraph nodes and state
    api/            - FastAPI routers
    core/           - Config and database setup
    knowledge_base/ - Policy documents for RAG
    llm/            - LLM client configuration
    models/         - SQLAlchemy ORM models
    rag/            - Embeddings, loader, retriever, vector store
    schemas/        - Pydantic schemas
    scripts/        - Data loading and seeding scripts
    services/       - Business logic (classifier, planner, ingestion, etc.)
    tools/          - Agent tool implementations
    utils/          - Health checks, benchmarks
  chroma_db/        - ChromaDB persistent storage
  alembic/          - Database migrations

frontend/
  src/
    api/            - Axios API client
    components/     - Reusable UI components
    pages/          - Route pages
    styles/         - Global styles
```

## License

MIT
