# 🌍 AI Travel Copilot

> A production-grade, portfolio-level AI Travel Copilot full-stack application built with **Flutter**, **Python / FastAPI**, **LangGraph**, **PostgreSQL + pgvector**, **Redis**, **RAG**, **Tool Calling**, and **Voice AI**.

---

## 🚀 Key Highlights

- 🤖 **LangGraph Multi-Step Travel Agent**: Stateful agentic workflow orchestrating intent understanding, missing info clarification, destination RAG retrieval, place search, weather check, distance calculation, budget estimation, and structured itinerary generation.
- 💬 **Conversational Itinerary Editing**: Modify day-by-day plans naturally (e.g. *"Make day 2 less busy"*, *"Add a beach sunset activity"*, *"Remove expensive restaurants"*).
- 📚 **Grounded RAG Pipeline**: Hybrid search (pgvector cosine similarity + full-text search) with cross-encoder reranking over rich destination guides.
- 🛠️ **Clean Tool Calling Suite**: 13 external tools for places, hotels, restaurants, weather, distance matrix, currency exchange, and trip modification.
- 📱 **Modern Flutter Mobile App**: Riverpod state management, GoRouter, timeline-based itinerary UI, interactive map with markers/polylines, dynamic chat cards, offline SQLite caching, and Voice STT/TTS.
- 💰 **Weather-Aware & Budget Optimization**: Dynamic adaptation to weather forecasts and multi-category budget tracking with over-budget alerts.
- 🛡️ **Production Security & Architecture**: JWT auth, Argon2 password hashing, rate limiting, audit logging, Pydantic v2 schemas, and Docker Compose deployment.

---

## 🏗️ Architecture Overview

```
Trabel app/
├── backend/                  # FastAPI async backend service
│   ├── app/
│   │   ├── agents/           # LangGraph state machine & nodes
│   │   ├── api/v1/           # REST & SSE endpoints
│   │   ├── core/             # Config, security, DB & Redis
│   │   ├── models/           # SQLAlchemy 2.0 async models
│   │   ├── schemas/          # Pydantic v2 schemas
│   │   ├── services/         # Business logic layer
│   │   ├── tools/            # Agent tool definitions
│   │   ├── rag/              # Ingestion, embeddings, vector store & reranker
│   │   └── integrations/     # Weather, Map, Currency external integrations
│   └── tests/                # Pytest unit & integration test suite
├── mobile/                   # Flutter mobile client
│   ├── lib/
│   │   ├── core/             # Theme, router, network client, local storage
│   │   ├── data/             # Models, datasources, repositories
│   │   ├── domain/           # Entities & business rules
│   │   ├── providers/        # Riverpod state notifiers
│   │   └── presentation/     # Screens (Chat, Timeline, Map, Budget, Profile)
│   └── test/                 # Flutter widget & unit tests
└── docs/                     # Architecture & workflow documentation
```

---

## ⚡ Getting Started

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# Activate virtual environment
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload --port 8000
```

### 2. Flutter Mobile Setup
```bash
cd mobile
flutter pub get
flutter run
```

---

## 👤 Author
- GitHub: [@imsalluu](https://github.com/imsalluu)
- Repository: [AI-Travel-Copilot-Mobile-App](https://github.com/imsalluu/AI-Travel-Copilot-Mobile-App)
