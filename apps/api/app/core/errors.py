"""
Veritas Standardized Exceptions & Error Schemas (PRD §9).
"""
from typing import Any, Dict, Optional


class VeritasError(Exception):
    """Base exception for all domain-specific Veritas errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.retry_after = retry_after
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.retry_after is not None:
            result["retry_after"] = self.retry_after
        if self.details:
            result["details"] = self.details
        return {"error": result}


class BadRequestError(VeritasError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(code="BAD_REQUEST", message=message, status_code=400, details=details)


class NotFoundError(VeritasError):
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(code="NOT_FOUND", message=message, status_code=404, details=details)


class RateLimitError(VeritasError):
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            status_code=429,
            retry_after=retry_after,
            details=details,
        )


class ServiceUnavailableError(VeritasError):
    def __init__(self, message: str = "Service unavailable", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            code="SERVICE_UNAVAILABLE",
            message=message,
            status_code=503,
            details=details,
        )
