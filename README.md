# AI Multi-Agent Orchestration Platform

An enterprise-grade, highly scalable AI Multi-Agent Orchestration Platform built with FastAPI (async database & memory channels) and Next.js 15.

This includes **Phase 2: AI Orchestration Core**. It adds a reusable LangGraph workflow foundation on top of the existing authentication, RBAC, database, Redis, and Docker setup. The phase uses only a deterministic Dummy Tool; it deliberately does not add business-domain agents, RAG, SQL, or web search.

---

## Architecture Overview

The system is configured as a monorepo consisting of:
1. **Backend Service (`backend/`)**: A FastAPI Python 3.12 application using asynchronous database calls via SQLAlchemy 2.0 (configured with `asyncpg` for PostgreSQL) and an asynchronous client connection wrapper for Redis.
2. **Frontend Service (`frontend/`)**: A Next.js 15 (React 19, TypeScript, TailwindCSS v4) dashboard utilizing glowing status indicators, and polling check gates.
3. **Infrastructure**: Multi-stage Docker environments, Docker Compose, and a CI validation workflow (GitHub Actions) checking formatting, coding standards, and running unit tests.

---

## Folder Structure

```
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI workflow
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/          # Health status and API v1 endpoints
│   │   │   └── dependencies.py  # Dependency injection declarations
│   │   ├── core/
│   │   │   ├── config.py        # Settings loader using pydantic-settings
│   │   │   ├── logging.py       # Structured logs configuration
│   │   │   └── security.py      # Access tokens creation and verification
│   │   ├── db/
│   │   │   ├── database.py      # SQLAlchemy 2.0 async engine and session
│   │   │   ├── models.py        # HealthCheck database model definition
│   │   │   └── session.py       # Async session provider
│   │   ├── agents/              # Future Agent architectures
│   │   ├── workflows/           # Future LangGraph stateful flows
│   │   ├── tools/               # Future Agent tooling
│   │   ├── memory/              # Future Short/Long-term memories
│   │   ├── services/            # Core business workflows
│   │   ├── utils/
│   │   │   └── redis.py         # Async Redis client connection wrapper
│   │   └── main.py              # Application entrypoint
│   ├── alembic/                 # Database schema migrations
│   ├── tests/                   # Pytest automation suite
│   ├── alembic.ini              # Alembic environment config
│   ├── Dockerfile               # Backend container recipe
│   └── requirements.txt         # Python package dependencies
├── frontend/
│   ├── app/                     # Page, theme, and layout configurations
│   ├── public/                  # Static assets
│   ├── package.json             # NPM project metadata
│   └── tsconfig.json            # TypeScript configuration
├── docker-compose.yml           # Multi-container local orchestration
├── pytest.ini                   # Python testing paths config
└── README.md                    # System documentation
```

---

## Environment Variables

Configure these variables inside `backend/.env`. Refer to `backend/.env.example` for details:

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `APP_ENV` | Application environment state | `development` |
| `SECRET_KEY` | Secret key used to encrypt and verify JWT tokens | `generate-a-secure-secret-key-here` |
| `POSTGRES_HOST` | Database server address | `localhost` (docker: `postgres`) |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_DB` | PostgreSQL database name | `platform_db` |
| `POSTGRES_USER` | Database username | `postgres` |
| `POSTGRES_PASSWORD`| Database password | `postgres_secure_password` |
| `REDIS_URL` | Connection URL for Redis client | `redis://localhost:6379/0` (docker: `redis://redis:6379/0`) |
| `OPENAI_API_KEY` | Secret API key to call OpenAI endpoints | `your-openai-api-key-here` |

---

## Installation & Running Locally

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment file and adjust configuration values:
   ```bash
   cp .env.example .env
   ```
5. Run tests:
   ```bash
   pytest
   ```
6. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```

The API endpoints will be accessible at:
- Core Platform Root: `http://localhost:8000/`
- Health Check: `http://localhost:8000/health`
- Swagger UI Documentation: `http://localhost:8000/docs`

### Phase 2 orchestration API

Both endpoints preserve the existing JWT authentication and `chat:write` RBAC permission.

- `POST /api/v1/orchestrate` executes the workflow and returns its final response.
- `POST /api/v1/orchestrate/stream` emits Server-Sent Events for planning, tool execution, memory update, and completion. It uses the same event shape that future token streaming can extend.

Example request body:

```json
{
  "request": "Validate the orchestration pipeline",
  "conversation_id": "optional-client-conversation-id"
}
```

The default graph is `Planner -> Dummy Tool -> Memory -> Complete`. `MemoryService`
depends only on the `MemoryStore` abstraction, so an in-memory implementation can be
replaced with Redis or a vector-backed adapter without changing graph nodes. New tools
are registered through `ToolRegistry`, and new agents through `AgentRegistry`.

### Phase 3 tool registry

Every tool implements the shared async interface: `execute`, `validate`, `permissions`,
and `metadata`. The registry validates requests and enforces each tool's declared RBAC
permission before dispatch. The initial registered capabilities are `dummy`,
`web_search`, `sql`, `email`, and `rag`; the Phase 3 providers are deterministic
adapters only and make no network, database, or email side effects. The planner selects
one of these tools from intent keywords and executes it through the registry.

### Phase 4 memory

`MemoryService` now loads conversation history before planning and persists both
messages and the latest workflow checkpoint after execution. `RedisMemoryStore` is the
short-term adapter (conversation messages plus expiring workflow state), while
`PostgresMemoryStore` is a repository adapter for durable history and user preference
storage. The latter receives a repository so deployments can choose their existing
PostgreSQL schema without coupling LangGraph nodes to SQLAlchemy models.

Planner context resolves simple references against the latest assistant result. After
`Generate sales report`, a follow-up `Email it` is planned as an email operation
containing the previous result. A vector database can be added as another `MemoryStore`
implementation without changing the workflow or planner contracts.

---

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```

The frontend client dashboard will be accessible at `http://localhost:3000`.

---

## Running with Docker Compose

To spin up the entire stack including Python Backend, PostgreSQL, and Redis containers in an isolated network environment:

1. Build and run all services:
   ```bash
   docker-compose up --build
   ```
2. Run database migrations:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

---

## Future Roadmap

- **Phase 2: Agent Architecture**: Build generic Agent classes, integrate OpenAI structured tools, and configure memory stores.
- **Phase 3: Multi-Agent Workflows**: Introduce state management, routers, and cooperative workflows via LangGraph.
- **Phase 4: Agent Observability**: Integrate LangSmith dashboards, tracing, evaluation runs, and UI controls for execution history.
