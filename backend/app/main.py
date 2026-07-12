from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.middleware import CoreMiddleware
from app.core.logging import logger
from app.core.exceptions import AppException
from app.utils.redis import redis_client
from app.api.routes.health import router as health_router
from app.api.routes.v1 import router as v1_router
from app.schemas.responses import APIResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events handler for the FastAPI application."""
    logger.info("Initializing AI Orchestration Platform Backend services...")

    # Establish Redis connection
    try:
        await redis_client.connect()
    except Exception as e:
        logger.error(f"Error during Redis startup connection: {str(e)}")

    # Seed default roles and permissions
    try:
        from app.db.database import SessionLocal
        from app.db.seeder import seed_database
        async with SessionLocal() as db_session:
            await seed_database(db_session)
    except Exception as e:
        logger.error(f"Error during database seeding at startup: {str(e)}")

    yield


    # Teardown Redis connection
    logger.info("Shutting down AI Orchestration Platform Backend services...")
    try:
        await redis_client.disconnect()
    except Exception as e:
        logger.error(f"Error during Redis shutdown: {str(e)}")


app = FastAPI(
    title="AI Multi-Agent Orchestration Platform",
    description="Core backend for managing multi-agent orchestrations, tasks, and memories.",
    version="1.0.0",
    lifespan=lifespan,
)

# Core middleware managing Correlation IDs, execution timings, and security headers
app.add_middleware(CoreMiddleware)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Exception handler for custom domain exceptions (database, agent, tool, workflow)."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "data": exc.details,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches all unhandled exceptions and returns standardized error APIResponse."""
    logger.error(
        f"Unhandled error on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred. Please contact system administrator.",
            "data": str(exc) if settings.APP_ENV == "development" else None,
        },
    )


# Root health routers
app.include_router(health_router)

# Versioned API routes
app.include_router(v1_router, prefix="/api/v1")


@app.get("/", response_model=APIResponse[dict[str, str]])
async def read_root() -> APIResponse[dict[str, str]]:
    """Root endpoint verifying application status and metadata."""
    return APIResponse(
        success=True,
        message="FastAPI platform router successfully reachable.",
        data={"status": "ok", "service": "AI Orchestration Platform"},
    )
