# 🏗️ AI Travel Copilot - System Architecture

## Overview
AI Travel Copilot is a modern, full-stack travel assistant platform designed for high responsiveness, grounded AI reasoning, rich interactive timeline itineraries, multi-modal voice AI, and offline readiness.

```
┌─────────────────────────────────────────────────────────────┐
│                     Flutter Mobile App                      │
│ (Riverpod + GoRouter + Dio + flutter_map + Offline Cache)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST / SSE
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Gateway & Auth                   │
│          (JWT Auth, Rate Limiting, Audit Logging)           │
└───────┬──────────────────────┬──────────────────────┬───────┘
        │                      │                      │
┌───────▼──────────────┐ ┌─────▼────────────────┐ ┌───▼───────┐
│ LangGraph AI Agent   │ │ Destination RAG      │ │ Weather & │
│ - Intent Parsing     │ │ - Chunking Pipeline  │ │ Distance  │
│ - 14 Travel Tools    │ │ - pgvector Embeddings│ │ Service   │
│ - Itinerary Synthesizer│ - Cosine/BM25 Hybrid │ │ (Open-    │
│ - Conversational Edit│ │ - Cross-Reranker     │ │  Meteo)   │
└───────┬──────────────┘ └─────┬────────────────┘ └───┬───────┘
        │                      │                      │
┌───────▼──────────────────────▼──────────────────────▼───────┐
│             PostgreSQL (pgvector) + Redis Cache             │
└─────────────────────────────────────────────────────────────┘
```

## Key Architectural Highlights

### 1. LangGraph State Machine Workflow
- **Intent Understanding**: Classifies user query (full planning, modification, inquiry, budget check).
- **Missing Information Interceptor**: Validates core parameters before calling expensive tools.
- **RAG Destination Grounding**: Pulls verified cultural, transit, and safety rules.
- **Tool Suite Execution**: Searches places, calculates transit times, polls real-time weather forecasts, and creates budget splits.
- **Structured Pydantic Models**: Guarantees typed, valid JSON outputs (`StructuredItineraryPlan`).
- **Conversational Delta Engine**: Applies conversational modifications ("Make day 2 less busy") directly to existing structured trees without resetting.

### 2. Grounded RAG Pipeline
- Text parser with 600-character chunking and 100-character overlap.
- Multi-provider embedding generator (OpenAI text-embedding-3-small + deterministic fallback).
- Hybrid search: pgvector cosine similarity score (70%) + exact keyword relevance density (30%).
- Full metadata tracking (source, category, section).

### 3. Flutter Mobile Architecture
- **State Management**: Flutter Riverpod with clean separation between Data -> Repositories -> Providers -> UI.
- **Navigation**: GoRouter with auth state preservation across 15 dedicated routes.
- **Theme**: Luxury obsidian dark mode with ocean teal accents, glassmorphism containers, and Outfit typography.
- **Offline Resilience**: Local caching of trips and chat history in SQLite / SharedPreferences.
