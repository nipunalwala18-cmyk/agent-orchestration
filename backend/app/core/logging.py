import logging
import sys
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure structured logging with standard stream handler
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}',
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("platform")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request and response logging in FastAPI."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        client_host = request.client.host if request.client else "unknown"
        logger.info(
            f"Incoming request | Method: {request.method} | Path: {request.url.path} | IP: {client_host}"
        )

        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000
            logger.info(
                f"Request completed | Method: {request.method} | Path: {request.url.path} | "
                f"Status: {response.status_code} | Duration: {duration:.2f}ms"
            )
            return response
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed | Method: {request.method} | Path: {request.url.path} | "
                f"Error: {str(e)} | Duration: {duration:.2f}ms",
                exc_info=True,
            )
            raise e
