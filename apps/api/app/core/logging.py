"""
Veritas Structured JSON Logging Engine
Outputs single-line JSON log events with correlation IDs.
"""
import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable preserving request correlation ID across async tasks
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
logger = logging.getLogger("veritas.access")


class StructuredJSONFormatter(logging.Formatter):
    """Formats log records as serialized JSON strings."""

    def format(self, record: logging.LogRecord) -> str:
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_ctx.get() or getattr(record, "request_id", None),
        }

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        standard_attrs = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process"
        }
        for key, val in record.__dict__.items():
            if key not in standard_attrs and key not in log_payload:
                log_payload[key] = val

        return json.dumps(log_payload)


def setup_logging(level: str = "INFO") -> None:
    """Configures root logger with StructuredJSONFormatter."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]

    # Silence overly noisy loggers
    logging.getLogger("uvicorn.access").handlers = []


def get_logger(name: str = "veritas") -> logging.Logger:
    """Returns a logger instance configured for structured logging."""
    return logging.getLogger(name)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Intercepts requests, assigns/propagates X-Request-ID, and outputs structured access logs."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        req_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        token = request_id_ctx.set(req_id)
        start_time = time.perf_counter()

        try:
            response: Response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            response.headers["X-Request-ID"] = req_id

            logger.info(
                f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "client_ip": request.client.host if request.client else "unknown",
                }
            )
            return response
        except Exception:
            raise
        finally:
            request_id_ctx.reset(token)
