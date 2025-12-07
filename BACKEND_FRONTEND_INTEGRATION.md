# Backend-Frontend Integration Guide

## Overview

The frontend is now properly connected to the backend API. The system provides:

- **API Client** (`src/utils/apiClient.js`): Unified interface for all backend API calls
- **Custom Hooks** (`src/utils/useApi.js`): React hooks for managing API state and side effects
- **ChatWidget** (`src/components/ChatWidget.tsx`): AI-powered Q&A interface integrated into documentation
- **Environment Configuration** (`.env.local`): Configurable API endpoint and timeout

## Architecture

### Frontend → Backend Communication

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (3000)                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         ChatWidget & Page Components (TSX)          │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │ uses                                    │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │      Custom Hooks (useApi.ts)                        │   │
│  │  • useHealthCheck()                                  │   │
│  │  • useRetrieve()                                     │   │
│  │  • useAnswer()                                       │   │
│  │  • useFeedback()                                     │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │ calls                                   │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │      API Client (apiClient.js)                       │   │
│  │  • health()                                          │   │
│  │  • retrieve(query, topK)                             │   │
│  │  • answer(question, conversationHistory)             │   │
│  │  • feedback(questionId, answerId, rating, feedback) │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │ HTTP/JSON                               │
└─────────────────────┼───────────────────────────────────────┘
                      │
                  CORS Enabled
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Backend (8000)                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              FastAPI Application                     │   │
│  │                                                      │   │
│  │  ┌─ GET  /health                                     │   │
│  │  ├─ POST /api/retrieve    → Qdrant                   │   │
│  │  ├─ POST /api/answer      → LLM + Qdrant             │   │
│  │  └─ POST /api/feedback    → PostgreSQL               │   │
│  │                                                      │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│        ┌────────────┼────────────┬──────────────┐            │
│        │            │            │              │            │
│    ┌───▼──┐   ┌─────▼────┐   ┌──▼────┐   ┌────▼─┐           │
│    │  DB  │   │  Qdrant  │   │ Redis │   │ LLM  │           │
│    │(5432)│   │(6333-34) │   │(6379) │   │(API) │           │
│    └──────┘   └──────────┘   └───────┘   └──────┘           │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Setup Instructions

### 1. Start Backend Services

```bash
# Start all Docker services
docker compose up -d

# Verify services are running
docker compose ps
```

Expected output:
```
NAME              STATUS           PORTS
textbook_postgres UP (healthy)     0.0.0.0:5432->5432/tcp
textbook_qdrant   UP               0.0.0.0:6333-6334->6333-6334/tcp
textbook_redis    UP               0.0.0.0:6379->6379/tcp
textbook_backend  UP (healthy)     0.0.0.0:8000->8000/tcp
```

### 2. Start Frontend Dev Server

```bash
cd frontend
npm start
```

Frontend will be available at: `http://localhost:3000`

### 3. Verify Connection

Open browser to `http://localhost:3000` and look for:

- **Blue Chat Button** (bottom-right corner with 💬 emoji)
- **Status Indicator** (✅ next to "AI Tutor" if connected)
- **Integration Test** (on any page to see test results)

## API Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Purpose:** Verify backend is running and database connections are healthy

**Response:**
```json
{
  "status": "ok",
  "database": "connected",
  "qdrant": "connected"
}
```

**Frontend Hook:**
```typescript
const { healthy, error, check } = useHealthCheck();
```

### 2. Retrieve Documents

**Endpoint:** `POST /api/retrieve`

**Purpose:** Search knowledge base for relevant documents

**Request:**
```json
{
  "query": "How to create a ROS 2 publisher?",
  "top_k": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "document": "module-01-ros2/02-nodes-topics-services.md",
      "score": 0.92,
      "content": "Publishers send messages to topics...",
      "metadata": { "module": "1" }
    }
  ]
}
```

**Frontend Hook:**
```typescript
const { data, loading, error, retrieve } = useRetrieve();
const result = await retrieve('query string', topK);
```

### 3. Get Answer with Citations

**Endpoint:** `POST /api/answer`

**Purpose:** Generate AI answer with source citations from knowledge base

**Request:**
```json
{
  "question": "What is a ROS 2 publisher?",
  "conversation_history": []
}
```

**Response:**
```json
{
  "answer": "A ROS 2 publisher is an entity that sends messages...",
  "citations": [
    {
      "title": "Nodes, Topics & Services",
      "url": "/docs/module-01-ros2/nodes-topics-services#publishers",
      "document": "module-01-ros2/02-nodes-topics-services.md"
    }
  ],
  "confidence": 0.88
}
```

**Frontend Hook:**
```typescript
const { data, loading, error, answer } = useAnswer();
const result = await answer('question');
// Automatic conversation history management
```

### 4. Submit Feedback

**Endpoint:** `POST /api/feedback`

**Purpose:** Record user feedback on answer quality

**Request:**
```json
{
  "question_id": "q-123",
  "answer_id": "a-456",
  "rating": 5,
  "feedback": "Very helpful and accurate!"
}
```

**Response:**
```json
{
  "status": "recorded",
  "id": "feedback-789"
}
```

**Frontend Hook:**
```typescript
const { loading, error, success, submit } = useFeedback();
await submit(questionId, answerId, rating, feedbackText);
```

## Environment Configuration

File: `frontend/.env.local`

```env
# API Base URL (default: http://localhost:8000)
REACT_APP_API_BASE_URL=http://localhost:8000

# Request timeout in milliseconds (default: 30000)
REACT_APP_API_TIMEOUT=30000
```

## ChatWidget Usage

### Display

The ChatWidget is automatically rendered on all pages at bottom-right corner.

- **Status Indicator:** ✅ (connected) or ⚠️ (backend unavailable)
- **Blue Chat Button:** Click to open/close conversation
- **Auto-scroll:** Messages automatically scroll to latest

### Features

1. **Natural Language Q&A**
   - Ask questions about any course content
   - Multi-turn conversations
   - Automatic context management

2. **Source Citations**
   - Each answer includes links to source materials
   - Click citations to navigate to relevant section
   - Track learning sources

3. **Real-time Status**
   - Shows connection status
   - Loading indicators during processing
   - Error messages if backend unavailable

4. **Conversation History**
   - Maintains context within session
   - Clear history button available
   - Auto-resets on page refresh

### Example Interactions

**Basic Q&A:**
```
User: "What is ROS 2?"
AI: "ROS 2 is a flexible middleware for writing robotic software..."
     [Source: Module 1 Introduction]
```

**Follow-up Question:**
```
User: "How do I publish to a topic?"
AI: "You create a Publisher object with the create_publisher method..."
     [Source: Nodes, Topics & Services]
```

## Troubleshooting

### ChatWidget Not Visible

1. **Check Backend Status:**
   ```bash
   docker compose logs backend
   curl http://localhost:8000/health
   ```

2. **Check Browser Console:**
   Open DevTools (F12) → Console tab for errors

3. **Verify CORS Configuration:**
   ```bash
   docker compose exec backend cat app/config.py | grep cors_origins
   ```

### Answers Not Generated

1. **Check Qdrant Connection:**
   ```bash
   curl http://localhost:6333/health
   ```

2. **Verify Content Indexed:**
   ```bash
   docker compose exec backend python scripts/ingest_to_qdrant.py --docs ../frontend/docs --collection physical_ai_humanoid_robotics_course
   ```

3. **Check API Logs:**
   ```bash
   docker compose logs backend --tail 50
   ```

### Slow Responses

1. **Check Backend Performance:**
   ```bash
   docker compose exec backend python -c "import psutil; print(psutil.virtual_memory())"
   ```

2. **Increase Timeout (if needed):**
   Edit `.env.local`:
   ```env
   REACT_APP_API_TIMEOUT=60000
   ```

3. **Monitor Logs:**
   ```bash
   docker compose logs -f backend
   ```

## Development Tips

### Adding New API Endpoints

1. **Add to Backend** (`backend/app/main.py`):
   ```python
   @app.post("/api/new-endpoint")
   async def new_endpoint(request: Request):
       return {"result": "data"}
   ```

2. **Add to Frontend Client** (`frontend/src/utils/apiClient.js`):
   ```javascript
   newEndpoint: (param) => apiFetch('/api/new-endpoint', {
     method: 'POST',
     body: JSON.stringify({ param }),
   }),
   ```

3. **Add Hook** (`frontend/src/utils/useApi.js`):
   ```typescript
   export const useNewEndpoint = () => {
     // Similar pattern to existing hooks
   };
   ```

### Testing Connection Locally

```bash
# Test health
curl http://localhost:8000/health

# Test retrieve
curl -X POST http://localhost:8000/api/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "ROS 2", "top_k": 5}'

# Test answer
curl -X POST http://localhost:8000/api/answer \
  -H "Content-Type: application/json" \
  -d '{"question": "What is ROS 2?", "conversation_history": []}'
```

## Performance Metrics

Expected performance with Docker Compose locally:

| Operation | Latency | Notes |
|-----------|---------|-------|
| Health Check | 50-100ms | Checks DB connections |
| Retrieve (5 docs) | 200-500ms | Vector search in Qdrant |
| Generate Answer | 2-5s | LLM inference + retrieval |
| Submit Feedback | 100-200ms | Database write |

## Security Considerations

### CORS

- Frontend: `http://localhost:3000` ✅
- Backend: `http://localhost:8000` ✅
- Production: Update `CORS_ORIGINS` environment variable

### API Keys

- Sensitive keys (LLM API, etc.) stored in Docker environment
- Never commit `.env.local` with real credentials
- Use GitHub Secrets for CI/CD

### Data Privacy

- Conversation history stored in browser session memory
- No persistent conversation history in current MVP
- User feedback stored anonymously

## Next Steps

1. **Content Indexing:**
   ```bash
   docker compose exec backend python scripts/ingest_to_qdrant.py --docs ../frontend/docs --collection physical_ai_humanoid_robotics_course
   ```

2. **Run Tests:**
   ```bash
   docker compose exec backend pytest backend/tests/acceptance/ -v
   ```

3. **Customize:**
   - Update styling in `src/components/ChatWidget.module.css`
   - Add more hooks in `src/utils/useApi.js`
   - Extend ChatWidget in `src/components/ChatWidget.tsx`

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docusaurus Integration](https://docusaurus.io/docs/plugins)
- [Qdrant Vector Database](https://qdrant.tech/)
- [React Hooks](https://react.dev/reference/react/hooks)
