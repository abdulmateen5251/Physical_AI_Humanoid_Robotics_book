# Physical AI & Humanoid Robotics Textbook with RAG Chatbot

[![Build Status](https://github.com/yourusername/physical-ai-textbook/workflows/CI/badge.svg)](https://github.com/yourusername/physical-ai-textbook/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Content License: CC BY-SA 4.0](https://img.shields.io/badge/Content%20License-CC%20BY--SA%204.0-lightgrey.svg)](http://creativecommons.org/licenses/by-sa/4.0/)

An AI-native textbook for learning Physical AI and Humanoid Robotics, featuring an embedded RAG (Retrieval-Augmented Generation) chatbot for interactive Q&A.

## 🚀 Features

- **Interactive RAG Chatbot**: Ask questions about course content with AI-powered answers
- **Full-book & Selection Mode**: Get answers from entire textbook or constrained to selected text
- **User Authentication**: Sign up/sign in with Better-Auth for personalized experience
- **Content Personalization**: Adapt chapters to your background and difficulty level

- **4 Course Modules**: 
  - Module 1: ROS 2 Fundamentals
  - Module 2: Digital Twin (Gazebo, Unity)
  - Module 3: NVIDIA Isaac Sim
  - Module 4: Vision-Language-Action Integration

## 📚 Quick Start

See [quickstart.md](specs/001-ai-textbook-rag-chatbot/quickstart.md) for detailed setup instructions.

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- OpenAI API key
- Qdrant Cloud account
- Neon Postgres account

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/physical-ai-textbook.git
   cd physical-ai-textbook
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start Services**
   ```bash
   cd ..
   docker-compose up -d postgres qdrant redis
   ```

4. **Run Database Migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

5. **Start Backend**
   ```bash
   uvicorn app.main:app --reload
   # API available at http://localhost:8000
   ```

6. **Frontend Setup** (in new terminal)
   ```bash
   cd frontend
   npm install
   npm start
   # Site available at http://localhost:3000
   ```

7. **Index Content**
   ```bash
   cd backend
   python scripts/ingest_to_qdrant.py --docs ../frontend/docs --collection physical_ai_humanoid_robotics_course
   ```

## 🏗️ Architecture

```
┌─────────────────┐
│  Docusaurus UI  │ ← React components, MDX content
└────────┬────────┘
         │
         ↓ REST API
┌─────────────────┐
│   FastAPI       │ ← RAG orchestration, LLM agents
│   Backend       │
└────┬───────┬────┘
     │       │
     ↓       ↓
┌─────────┐ ┌──────────┐
│ Qdrant  │ │  Neon    │
│ Vectors │ │ Postgres │
└─────────┘ └──────────┘
```

## 📖 Documentation

- [Full Specification](specs/001-ai-textbook-rag-chatbot/spec.md)
- [Implementation Plan](specs/001-ai-textbook-rag-chatbot/plan.md)
- [Task Breakdown](specs/001-ai-textbook-rag-chatbot/tasks.md)
- [Data Model](specs/001-ai-textbook-rag-chatbot/data-model.md)
- [API Contracts](specs/001-ai-textbook-rag-chatbot/contracts/openapi.yaml)
- [Contributing Guide](CONTRIBUTING.md)

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/unit/ -v                    # Unit tests
pytest tests/integration/ -v             # Integration tests
pytest tests/acceptance/ -v              # RAG accuracy tests
pytest --cov=app --cov-report=html       # Coverage report
```

### Frontend Tests
```bash
cd frontend
npm test                                 # Unit tests
npm run test:e2e                         # E2E tests with Playwright
```

## 🚢 Deployment

### GitHub Pages (Frontend)
```bash
cd frontend
npm run build
npm run deploy
```

### Cloud Run (Backend)
```bash
cd backend
gcloud run deploy textbook-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

See [deployment.md](docs/deployment.md) for detailed instructions.

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Create feature branch: `git checkout -b feat/your-feature`
2. Make changes following [coding standards](CONTRIBUTING.md#coding-standards)
3. Run tests: `pytest` and `npm test`
4. Commit with conventional commits: `feat(spec): add new feature (SPEC-020)`
5. Submit PR with [PR template](.github/PULL_REQUEST_TEMPLATE.md)

## 📄 License

- **Code**: MIT License - see [LICENSE](LICENSE)
- **Content**: CC BY-SA 4.0 - see [Content License](docs/content-license.md)

## 🙏 Acknowledgments

- Built for  Physical AI & Humanoid Robotics Course
- Powered by OpenAI GPT-4o, Anthropic Claude, LangChain
- Vector storage by Qdrant Cloud
- Database by Neon Serverless Postgres

## 📧 Contact

For questions or support, please open an issue or contact [your-email@example.com](mailto:your-email@example.com).

---

**Status**: 🚧 In Development (v0.1-alpha)

**Last Updated**: 2025-12-06
