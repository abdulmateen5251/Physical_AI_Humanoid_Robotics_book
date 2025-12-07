# API Documentation

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: TBD

## Authentication

Currently, API endpoints are open (no authentication required). Authentication will be added in Phase 5.

## Endpoints

### Health Check

#### `GET /health`

Check API health status.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "0.1.0"
}
```

---

### Retrieve Chunks

#### `POST /api/retrieve`

Retrieve relevant document chunks for a question without generating an answer. Useful for debugging retrieval quality or building custom LLM pipelines.

**Request Body**:
```json
{
  "question": "How do I create a ROS 2 node?",
  "top_k": 10,
  "module_filter": "module-01-ros2",
  "lang": "en"
}
```

**Parameters**:
- `question` (string, required): User question
- `top_k` (integer, optional, 1-50): Number of chunks to retrieve (default: 10)
- `module_filter` (string, optional): Filter by module ID (e.g., "module-01-ros2")
- `lang` (string, optional): Language filter, "en" or "ur" (default: "en")

**Response** (200 OK):
```json
{
  "chunks": [
    {
      "chunk_id": "chunk-001",
      "content": "To create a ROS 2 node in Python...",
      "chapter_id": "module-01-ros2",
      "section": "Creating Nodes",
      "heading_path": ["Introduction", "Creating Your First Node"],
      "file_url": "/docs/module-01-ros2/02-nodes-topics",
      "score": 0.92
    }
  ],
  "total": 10
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is ROS 2?",
    "top_k": 5
  }'
```

---

### Answer Question

#### `POST /api/answer`

Main RAG endpoint - generates an answer to a question using retrieved context or selected text.

**Request Body (Fullbook Mode)**:
```json
{
  "question": "How do I create a ROS 2 node?",
  "scope": "fullbook",
  "module_filter": "module-01-ros2",
  "top_k": 10,
  "user_id": "user-123"
}
```

**Request Body (Selection Mode)**:
```json
{
  "question": "What does this code do?",
  "scope": "selected_text",
  "selected_text": "import rclpy\nfrom rclpy.node import Node\n\nclass MyNode(Node):\n    def __init__(self):\n        super().__init__('my_node')"
}
```

**Parameters**:
- `question` (string, required): User question
- `scope` (string, optional): Query mode - "fullbook" or "selected_text" (default: "fullbook")
- `selected_text` (string, required if scope=selected_text): Text to analyze
- `module_filter` (string, optional): Filter retrieval by module
- `top_k` (integer, optional): Number of chunks to retrieve (default: 10)
- `user_id` (string, optional): User ID for personalization (Phase 5)

**Response** (200 OK):
```json
{
  "answer": "To create a ROS 2 node in Python, you need to...",
  "sources": [
    {
      "chapter_id": "module-01-ros2",
      "section": "Creating Nodes",
      "file_url": "/docs/module-01-ros2/02-nodes-topics",
      "heading_path": ["Introduction", "Creating Your First Node"],
      "score": 0.92
    }
  ],
  "chunk_ids": ["chunk-001", "chunk-002"],
  "retrieval_score_avg": 0.88,
  "response_time_ms": 1250,
  "scope": "fullbook"
}
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "selected_text required when scope=selected_text"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/answer \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is ROS 2?",
    "scope": "fullbook",
    "top_k": 5
  }'
```

---

### Submit Feedback

#### `POST /api/feedback`

Submit user feedback on a Q&A interaction to improve the system.

**Request Body**:
```json
{
  "session_id": "session-abc-123",
  "question": "How do I create a ROS 2 node?",
  "answer": "To create a ROS 2 node...",
  "rating": 5,
  "chunk_ids": ["chunk-001", "chunk-002"],
  "scope": "fullbook",
  "comment": "Very helpful answer!",
  "user_id": "user-123"
}
```

**Parameters**:
- `session_id` (string, optional): Session ID for tracking
- `question` (string, required): Original question
- `answer` (string, required): Generated answer
- `rating` (integer, required, 1-5): User rating (1=poor, 5=excellent)
- `chunk_ids` (array, optional): Retrieved chunk IDs
- `scope` (string, optional): Query scope (default: "fullbook")
- `comment` (string, optional): User comment
- `user_id` (string, optional): User ID

**Response** (200 OK):
```json
{
  "success": true,
  "feedback_id": 123,
  "message": "Feedback submitted successfully"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is ROS 2?",
    "answer": "ROS 2 is a middleware...",
    "rating": 5
  }'
```

---

### Feedback Statistics

#### `GET /api/feedback/stats`

Get aggregate feedback statistics (last 30 days).

**Response** (200 OK):
```json
{
  "total_feedback": 150,
  "avg_rating": 4.2,
  "positive_count": 120,
  "negative_count": 15,
  "unique_sessions": 75
}
```

**Example**:
```bash
curl http://localhost:8000/api/feedback/stats
```

---

## Error Responses

All endpoints may return these error responses:

**500 Internal Server Error**:
```json
{
  "detail": "Retrieval failed: Connection to Qdrant failed"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "rating"],
      "msg": "ensure this value is less than or equal to 5",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## Rate Limiting

- **Current**: No rate limiting (Phase 5)
- **Planned**: 60 requests/minute per IP

---

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Retrieve chunks
curl -X POST http://localhost:8000/api/retrieve \
  -H "Content-Type: application/json" \
  -d '{"question": "What is ROS 2?", "top_k": 3}'

# Answer question
curl -X POST http://localhost:8000/api/answer \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I create a publisher in rclpy?", "scope": "fullbook"}'
```

### Using Python

```python
import requests

# Answer question
response = requests.post(
    "http://localhost:8000/api/answer",
    json={
        "question": "What is ROS 2?",
        "scope": "fullbook",
        "top_k": 5
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])}")
```

### Interactive API Docs

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can test all endpoints directly in the browser.

---

## WebSocket Support (Phase 6)

Streaming answers via WebSocket will be added in Phase 6 for real-time response generation.

**Planned Endpoint**: `ws://localhost:8000/ws/chat`

---

## Status Codes

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error (check logs)

---

## Need Help?

- Check API logs: Backend logs show detailed request/response information
- Test retrieval quality: Use `/api/retrieve` to debug chunk relevance
- View API schema: See `specs/001-ai-textbook-rag-chatbot/contracts/openapi.yaml`
