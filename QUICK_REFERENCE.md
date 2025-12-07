# Quick Reference: Backend-Frontend Integration

## Files Created/Modified

### API Client Layer
- `frontend/src/utils/apiClient.js` - HTTP client with timeout handling
- `frontend/src/utils/useApi.js` - React hooks for API calls
- `frontend/.env.local` - API configuration

### Components
- `frontend/src/components/ChatWidget.tsx` - Main chat interface
- `frontend/src/components/ChatWidget.module.css` - ChatWidget styling
- `frontend/src/components/IntegrationTest.tsx` - Connection verification
- `frontend/src/theme/ChatWidgetPlugin.js` - Docusaurus plugin
- `frontend/src/theme/ChatWidgetWrapper.tsx` - Root wrapper component

### Configuration
- `frontend/docusaurus.config.js` - Added ChatWidget plugin

## Quick Start

```bash
# 1. Start backend
docker compose up -d

# 2. Start frontend
cd frontend && npm start

# 3. Open browser
# http://localhost:3000
# Look for blue 💬 button in bottom-right
```

## API Endpoints Reference

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/health` | GET | Check backend availability | ✅ Ready |
| `/api/retrieve` | POST | Search knowledge base | ✅ Ready |
| `/api/answer` | POST | Get AI answer with citations | ✅ Ready |
| `/api/feedback` | POST | Record user feedback | ✅ Ready |

## Frontend Hooks (Ready to Use)

```javascript
import { useHealthCheck, useRetrieve, useAnswer, useFeedback } from './utils/useApi';

// Check if backend is available
const { healthy, error, check } = useHealthCheck();

// Search documents
const { data, loading, error, retrieve } = useRetrieve();
await retrieve('search query', 5);

// Get AI answer
const { data, loading, error, answer } = useAnswer();
await answer('your question');

// Submit feedback
const { loading, error, success, submit } = useFeedback();
await submit(questionId, answerId, rating, 'feedback text');
```

## Environment Variables

**File:** `frontend/.env.local`

```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000
```

## Status Checks

```bash
# Backend health
curl http://localhost:8000/health

# Qdrant vector DB
curl http://localhost:6333/health

# Database
docker compose exec postgres pg_isready

# Frontend
# http://localhost:3000 (check browser console for errors)
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| ChatWidget shows ⚠️ | Backend not running: `docker compose up -d` |
| CORS errors in console | Check `.env.local` has correct `REACT_APP_API_BASE_URL` |
| No chat responses | Content not indexed. Run: `docker compose exec backend python scripts/ingest_to_qdrant.py --docs ../frontend/docs --collection physical_ai_humanoid_robotics_course` |
| Slow responses | Check backend logs: `docker compose logs -f backend` |
| Frontend not loading | Check dependencies: `cd frontend && npm install` |

## Testing the Connection

1. **Open ChatWidget:**
   - Click blue 💬 button bottom-right
   - Status shows ✅ (connected) or ⚠️ (disconnected)

2. **Ask a Question:**
   - Type: "What is ROS 2?"
   - Should receive answer with sources

3. **Check Console:**
   - Open DevTools (F12)
   - Check Network tab for API calls
   - Check Console for errors

## Architecture Summary

```
User Types in ChatWidget
         ↓
useAnswer Hook
         ↓
apiClient.answer()
         ↓
POST http://localhost:8000/api/answer
         ↓
FastAPI Backend
    • Retrieve similar docs from Qdrant
    • Get embeddings
    • Generate answer with LLM
         ↓
Response with citations
         ↓
Display in ChatWidget
```

## Next: Content Indexing

Before ChatWidget can answer questions, index content:

```bash
docker compose exec backend python scripts/ingest_to_qdrant.py \
  --docs ../frontend/docs \
  --collection physical_ai_humanoid_robotics_course
```

Expected output:
```
Indexing documents...
Found 2 markdown files
Embedded 2 documents
Collection created: physical_ai_humanoid_robotics_course
```

## Debugging

```bash
# View backend logs
docker compose logs -f backend

# Check if services are running
docker compose ps

# Test API endpoint directly
curl -X POST http://localhost:8000/api/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query":"ROS 2","top_k":5}'

# Check frontend errors
# Browser DevTools → Console tab
```

## Key Files for Developers

| File | Purpose | Edit When... |
|------|---------|--------------|
| `apiClient.js` | API configuration | Adding new endpoints |
| `useApi.js` | React hooks | Adding new hooks or state management |
| `ChatWidget.tsx` | Chat UI | Changing chat interface or styling |
| `ChatWidget.module.css` | Chat styling | Updating colors, layout, animations |
| `.env.local` | Configuration | Changing API URL or timeout |

## Performance Expectations

Local Docker environment:
- Health check: **50-100ms**
- Retrieve documents: **200-500ms**
- Generate answer: **2-5 seconds**
- Submit feedback: **100-200ms**

## Success Indicators

✅ Backend is working if:
- `docker compose ps` shows all services "Up"
- `curl http://localhost:8000/health` returns `{"status":"ok"}`

✅ Frontend is working if:
- `http://localhost:3000` loads without errors
- Blue chat button visible bottom-right
- Browser console has no CORS errors

✅ Connection is working if:
- ChatWidget shows ✅ status indicator
- You can type and receive responses
- Sources/citations appear in responses
