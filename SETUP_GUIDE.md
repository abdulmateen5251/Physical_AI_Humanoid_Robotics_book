# Setup Guide for Windows

## Prerequisites

1. **Python 3.11+** (You have 3.13.7 ✓)
2. **Node.js 18+** (For frontend)
3. **Docker Desktop** (For local services)
4. **Git** (For version control)

## Quick Start (Without Docker)

If you don't have Docker Desktop or want to test without it, you can use cloud services:

### Step 1: Install Dependencies

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
cd backend
uv pip install -r requirements.txt
cd ..
```

### Step 2: Configure Environment Variables

Edit `backend\.env` and add your API keys:

**Required for Phase 3 Testing:**
- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys
- `QDRANT_URL` - Use Qdrant Cloud (free tier): https://cloud.qdrant.io
- `QDRANT_API_KEY` - From Qdrant Cloud dashboard
- `DATABASE_URL` - Use Neon (free tier): https://neon.tech

**Example with cloud services:**
```env
OPENAI_API_KEY=sk-proj-abc123...
QDRANT_URL=https://xyz-abc.us-east.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=abc123...
DATABASE_URL=postgresql+asyncpg://user:pass@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb
```

### Step 3: Initialize Database

```powershell
cd backend
alembic upgrade head
```

### Step 4: Start the Server

```powershell
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Test the API

Open another terminal:

```powershell
# Test health endpoint
curl http://localhost:8000/health

# Open interactive API docs
Start-Process "http://localhost:8000/docs"
```

---

## Full Setup (With Docker Desktop)

### Step 1: Install Docker Desktop

1. Download from: https://www.docker.com/products/docker-desktop/
2. Install and restart your computer
3. Start Docker Desktop
4. Verify installation:
   ```powershell
   docker --version
   docker compose version  # Note: "docker compose" not "docker-compose"
   ```

### Step 2: Update docker-compose Command

Modern Docker Desktop uses `docker compose` (with space) instead of `docker-compose`:

```powershell
# Old command (doesn't work):
docker-compose up -d

# New command (works with Docker Desktop):
docker compose up -d postgres qdrant redis
```

### Step 3: Start Services

```powershell
# From project root
docker compose up -d postgres qdrant redis

# Check services are running
docker compose ps
```

### Step 4: Configure and Run Backend

```powershell
# Configure environment (edit .env with your keys)
cd backend
notepad .env  # Edit with your API keys

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

---

## Testing Without Docker (Recommended for Quick Start)

You can skip Docker entirely and use cloud services:

### 1. Qdrant Cloud (Vector Database)

1. Go to https://cloud.qdrant.io
2. Sign up (free tier available)
3. Create a cluster
4. Get your cluster URL and API key
5. Add to `.env`:
   ```
   QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
   QDRANT_API_KEY=your-api-key
   ```

### 2. Neon (Postgres Database)

1. Go to https://neon.tech
2. Sign up (free tier available)
3. Create a project
4. Copy connection string
5. Add to `.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://user:pass@host.neon.tech/dbname
   ```

### 3. Redis (Optional - Skip for Phase 3)

Redis is only needed for Phase 6 (Personalization). You can skip it for now.

---

## Troubleshooting

### Issue: "docker-compose not recognized"

**Solution**: Use `docker compose` (with space) or install Docker Desktop.

```powershell
# Instead of:
docker-compose up -d

# Use:
docker compose up -d
```

### Issue: "Alembic JSONDecodeError"

**Cause**: Missing or invalid `.env` file.

**Solution**: 
1. Copy `.env.example` to `.env`
2. Edit `.env` with valid values
3. For CORS_ORIGINS, use proper JSON array:
   ```
   CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
   ```

### Issue: "Cannot connect to Qdrant"

**Solution**: 
- If using Docker: Make sure `docker compose up -d qdrant` succeeded
- If using cloud: Check your QDRANT_URL and QDRANT_API_KEY
- Test connection: http://localhost:6333 (Docker) or your cloud URL

### Issue: "Cannot connect to Postgres"

**Solution**:
- If using Docker: Make sure `docker compose up -d postgres` succeeded
- If using cloud (Neon): Check your DATABASE_URL
- Verify format: `postgresql+asyncpg://user:pass@host:5432/dbname`

---

## Minimal Setup for Testing Phase 3

**What you actually need right now:**

1. ✅ Python environment (you have this)
2. ✅ Backend dependencies installed (you have this)
3. ⚠️ `.env` file with valid API keys (create this)
4. ⚠️ Qdrant instance (use cloud.qdrant.io - free)
5. ⚠️ Postgres instance (use neon.tech - free)
6. ❌ Redis (NOT needed until Phase 6)
7. ❌ Frontend (NOT needed until T039-T047)

**Minimal start command:**

```powershell
# 1. Edit .env
cd backend
notepad .env  # Add your API keys

# 2. Run migrations
alembic upgrade head

# 3. Start server
uvicorn app.main:app --reload

# 4. Test in another terminal
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

---

## Next Steps After Setup

1. **Create sample content** (T048-T049)
2. **Index content** to Qdrant:
   ```powershell
   python scripts/ingest_to_qdrant.py --docs ../docs --collection physical_ai_humanoid_robotics_course
   ```
3. **Test RAG pipeline**:
   ```powershell
   curl -X POST http://localhost:8000/api/answer `
     -H "Content-Type: application/json" `
     -d '{"question": "What is ROS 2?", "scope": "fullbook"}'
   ```

---

## Getting API Keys (Free Tiers)

### OpenAI API Key
- Sign up: https://platform.openai.com/signup
- Add payment method (required, but you get $5 free credit)
- Create API key: https://platform.openai.com/api-keys
- Cost: ~$0.02 per 1000 questions (very cheap for testing)

### Qdrant Cloud
- Sign up: https://cloud.qdrant.io
- Free tier: 1GB storage, 100k vectors
- Create cluster → Get API key
- Sufficient for the entire textbook

### Neon Postgres
- Sign up: https://neon.tech
- Free tier: 0.5GB storage, 1 database
- Create project → Copy connection string
- More than enough for user data

---

## Support

If you encounter issues:
1. Check logs: `uvicorn app.main:app --reload --log-level debug`
2. Verify `.env` file: `cat .env` (PowerShell: `Get-Content .env`)
3. Test services individually:
   - Qdrant: Visit your cluster URL in browser
   - Postgres: `psql <DATABASE_URL>`
   - API: `curl http://localhost:8000/health`
