"""Custom exceptions for Nutrient DWS client."""

from typing import Optional


class NutrientError(Exception):
    """Base exception for all Nutrient client errors."""

    pass


class AuthenticationError(NutrientError):
    """Raised when authentication fails (401/403 errors)."""

    pass


class APIError(NutrientError):
    """Raised for general API errors.

    Attributes:
        status_code: HTTP status code from the API.
        response_body: Raw response body from the API for debugging.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ) -> None:
        """Initialize APIError with status code and response body."""
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body