import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger


class CoreMiddleware(BaseHTTPMiddleware):
    """Core application middleware managing correlation IDs, execution timing, security headers, and structured logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Resolve or generate Correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        client_host = request.client.host if request.client else "unknown"

        # Log incoming request
        logger.info(
            {
                "message": f"Incoming request: {request.method} {request.url.path}",
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_host,
                "correlation_id": correlation_id,
                "event": "request_start",
            }
        )

        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000

            # Attach request tracking and timing response headers
            response.headers["X-Request-ID"] = correlation_id
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Process-Time"] = f"{duration:.2f}ms"

            # Attach HTTP security headers (OWASP best practices)
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

            # Log successful response
            logger.info(
                {
                    "message": f"Request completed: {request.method} {request.url.path} with status {response.status_code}",
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": client_host,
                    "status_code": response.status_code,
                    "duration_ms": round(duration, 2),
                    "correlation_id": correlation_id,
                    "event": "request_success",
                }
            )
            return response
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            # Log exception
            logger.error(
                {
                    "message": f"Request failed: {request.method} {request.url.path} - {str(e)}",
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": client_host,
                    "duration_ms": round(duration, 2),
                    "correlation_id": correlation_id,
                    "event": "request_failure",
                },
                exc_info=True,
            )
            raise e
