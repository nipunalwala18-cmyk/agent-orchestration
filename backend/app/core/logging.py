import json
import logging
import sys
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class JSONFormatter(logging.Formatter):
    """Custom formatter to format log records into structured JSON string formats."""

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
        }

        # Handle dictionary messages for structured logging
        if isinstance(record.msg, dict):
            log_record.update(record.msg)
        else:
            log_record["message"] = record.getMessage()

        # Handle exception information if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


# Configure logging handlers with the custom JSON formatter
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%S%z"))

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
# Clear existing default handlers to prevent duplicate formatting
root_logger.handlers = [handler]

logger = logging.getLogger("platform")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request and response logging in FastAPI."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        client_host = request.client.host if request.client else "unknown"
        correlation_id = getattr(request.state, "correlation_id", "unknown")

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
            logger.info(
                {
                    "message": f"Request completed with status {response.status_code}",
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
            logger.error(
                {
                    "message": f"Request failed: {str(e)}",
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
