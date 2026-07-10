# AI Multi-Agent Orchestration Platform

An enterprise-grade, highly scalable AI Multi-Agent Orchestration Platform built with FastAPI (async database & memory channels) and Next.js 15.

This is **Phase 1: Foundation Setup**. It establishes a clean monorepo codebase architecture, environment configs, security utilities, structured logging middleware, health-check status pathways, unit testing configurations, and Docker integration.

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
