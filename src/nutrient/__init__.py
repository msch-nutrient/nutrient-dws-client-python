"""Nutrient DWS Python Client.

A Python client library for the Nutrient Document Web Services API.
"""

from nutrient.client import NutrientClient
from nutrient.exceptions import (
    APIError,
    AuthenticationError,
    FileProcessingError,
    NutrientError,
    TimeoutError,
    ValidationError,
)

__version__ = "0.1.0"
__all__ = [
    "APIError",
    "AuthenticationError",
    "FileProcessingError",
    "NutrientClient",
    "NutrientError",
    "TimeoutError",
    "ValidationError",
]
