"""Unit tests for exceptions module."""

from nutrient_dws.exceptions import (
    APIError,
    AuthenticationError,
    FileProcessingError,
    NutrientError,
    NutrientTimeoutError,
    ValidationError,
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


def test_api_error_basic():
    """Test API error without additional context."""
    exc = APIError("API request failed")
    assert str(exc) == "API request failed"
    assert isinstance(exc, NutrientError)
    assert exc.status_code is None
    assert exc.response_body is None
    assert exc.request_id is None


def test_api_error_with_status():
    """Test API error with status code."""
    exc = APIError("Not found", status_code=404)
    assert exc.status_code == 404
    assert "Status: 404" in str(exc)


def test_api_error_full_context():
    """Test API error with all context."""
    exc = APIError(
        "Server error",
        status_code=500,
        response_body='{"error": "Internal server error"}',
        request_id="req-123",
    )
    assert exc.status_code == 500
    assert exc.response_body == '{"error": "Internal server error"}'
    assert exc.request_id == "req-123"
    assert "Status: 500" in str(exc)
    assert "Request ID: req-123" in str(exc)
    assert "Response:" in str(exc)


def test_validation_error():
    """Test validation error."""
    exc = ValidationError("Invalid input")
    assert str(exc) == "Invalid input"
    assert isinstance(exc, NutrientError)
    assert exc.errors == {}


def test_validation_error_with_details():
    """Test validation error with error details."""
    errors = {"field": "Invalid value"}
    exc = ValidationError("Validation failed", errors=errors)
    assert exc.errors == errors


def test_timeout_error():
    """Test timeout error."""
    exc = NutrientTimeoutError("Request timed out")
    assert str(exc) == "Request timed out"
    assert isinstance(exc, NutrientError)


def test_file_processing_error():
    """Test file processing error."""
    exc = FileProcessingError("Failed to process file")
    assert str(exc) == "Failed to process file"
    assert isinstance(exc, NutrientError)
