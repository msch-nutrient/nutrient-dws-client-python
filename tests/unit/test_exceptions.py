"""Unit tests for exceptions module."""

from nutrient_dws.exceptions import (
    APIError,
    AuthenticationError,
    NutrientError,
)


def test_nutrient_error():
    """Test base exception."""
    exc = NutrientError("Test error")
    assert str(exc) == "Test error"
    assert isinstance(exc, Exception)


def test_authentication_error():
    """Test authentication error."""
    exc = AuthenticationError("Invalid API key")
    assert str(exc) == "Invalid API key"
    assert isinstance(exc, NutrientError)


def test_api_error():
    """Test API error."""
    exc = APIError("API request failed")
    assert str(exc) == "API request failed"
    assert isinstance(exc, NutrientError)
