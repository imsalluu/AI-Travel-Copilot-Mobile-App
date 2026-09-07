# 🌐 AI Travel Copilot - REST & Realtime API Specification

Base URL: `http://localhost:8000/api/v1`

## 1. Authentication (`/auth`)
- `POST /auth/register` — Register a new user and generate JWT tokens.
- `POST /auth/login` — Authenticate user via email/password.
- `POST /auth/refresh` — Issue fresh access token from refresh token.
- `GET /auth/me` — Return current authenticated user profile & travel preferences.

## 2. User & Preferences (`/users`)
- `PUT /users/me` — Update user profile details.
- `GET /users/me/preferences` — Get travel persona (budget tier, dietary, pace, transport).
- `PUT /users/me/preferences` — Update travel persona memory.

## 3. Trips (`/trips`)
- `GET /trips` — List user trips with status filter (`DRAFT`, `PLANNED`, `ACTIVE`, `COMPLETED`, `ARCHIVED`).
- `POST /trips` — Create a new trip.
- `GET /trips/{trip_id}` — Get trip by ID with days and activities eagerly loaded.
- `PUT /trips/{trip_id}` — Update trip details or toggle favorite.
- `DELETE /trips/{trip_id}` — Delete a trip.
- `POST /trips/{trip_id}/duplicate` — Clone a trip and all its day schedules.
- `GET /trips/saved-places/all` — List saved bookmarks.
- `POST /trips/saved-places` — Bookmark a place.

## 4. Itinerary Timeline (`/itinerary`)
- `POST /itinerary/trips/{trip_id}/days/{day_id}/activities` — Add activity to day.
- `PUT /itinerary/activities/{activity_id}` — Edit activity or mark completed.
- `DELETE /itinerary/activities/{activity_id}` — Remove activity from day.
- `POST /itinerary/reorder` — Reorder activities in a day.
- `POST /itinerary/move` — Move activity across days.

## 5. AI Chat & Copilot (`/chat`)
- `POST /chat/message` — Send natural language prompt to LangGraph agent (returns markdown + structured cards).
- `GET /chat/conversations` — List conversation history.
- `GET /chat/conversations/{id}` — Get conversation messages.
- `DELETE /chat/conversations/{id}` — Delete conversation.

## 6. Weather (`/weather`)
- `GET /weather` — Get destination weather forecast, rain probability, and AI advisories.

## 7. Budget & Expenses (`/budget`)
- `GET /budget/trips/{trip_id}` — Get budget summary with category allocations and over-budget warnings.
- `PUT /budget/trips/{trip_id}` — Update category allocations.
- `POST /budget/trips/{trip_id}/expenses` — Log actual expense.
- `DELETE /budget/expenses/{expense_id}` — Delete expense.

## 8. Maps & Routing (`/maps`)
- `POST /maps/calculate-route` — Compute distance, duration, and route polyline waypoints.

## 9. RAG Knowledge (`/knowledge`)
- `POST /knowledge/search` — Search grounded guides with hybrid vector retrieval.
- `POST /knowledge/documents` — Ingest guide document.

## 10. Voice AI (`/voice`)
- `POST /voice/process-audio` — Speech-to-Text audio transcription & AI agent dispatch.
- `POST /voice/synthesize-speech` — Text-to-Speech audio generation.
