import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger


class CoreMiddleware(BaseHTTPMiddleware):
    """Core application middleware managing correlation IDs, execution timing, and security headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Resolve or generate Correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        client_host = request.client.host if request.client else "unknown"
        logger.info(
            f"Correlation ID: {correlation_id} | Request: {request.method} {request.url.path} | IP: {client_host}"
        )

        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000

            # Attach request tracking and timing response headers
            response.headers["X-Request-ID"] = correlation_id
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Process-Time"] = f"{duration:.2f}ms"

            # Attach HTTP security best practices headers
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

            logger.info(
                f"Correlation ID: {correlation_id} | Completed: {request.method} {request.url.path} | "
                f"Status: {response.status_code} | Duration: {duration:.2f}ms"
            )
            return response
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"Correlation ID: {correlation_id} | Failed: {request.method} {request.url.path} | "
                f"Error: {str(e)} | Duration: {duration:.2f}ms",
                exc_info=True,
            )
            raise e
