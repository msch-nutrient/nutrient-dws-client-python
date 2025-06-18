"""Unit tests for custom exceptions."""

from nutrient_dws.exceptions import (
    APIError,
    AuthenticationError,
    FileProcessingError,
    NutrientError,
    NutrientTimeoutError,
    ValidationError,
)


class TestNutrientError:
    """Test base exception class."""

    def test_inheritance(self):
        """Test that NutrientError inherits from Exception."""
        assert issubclass(NutrientError, Exception)

    def test_instantiation(self):
        """Test basic instantiation."""
        exc = NutrientError("Test error")
        assert str(exc) == "Test error"


class TestAuthenticationError:
    """Test authentication error."""

    def test_inheritance(self):
        """Test that AuthenticationError inherits from NutrientError."""
        assert issubclass(AuthenticationError, NutrientError)

    def test_default_message(self):
        """Test default error message."""
        exc = AuthenticationError()
        assert str(exc) == "Authentication failed"

    def test_custom_message(self):
        """Test custom error message."""
        exc = AuthenticationError("Invalid API key")
        assert str(exc) == "Invalid API key"


class TestAPIError:
    """Test API error with rich context."""

    def test_inheritance(self):
        """Test that APIError inherits from NutrientError."""
        assert issubclass(APIError, NutrientError)

    def test_basic_error(self):
        """Test basic error without additional context."""
        exc = APIError("Something went wrong")
        assert str(exc) == "Something went wrong"
        assert exc.status_code is None
        assert exc.response_body is None
        assert exc.request_id is None

    def test_error_with_status(self):
        """Test error with status code."""
        exc = APIError("Not found", status_code=404)
        assert exc.status_code == 404
        assert str(exc) == "Not found | Status: 404"

    def test_error_with_all_context(self):
        """Test error with all context fields."""
        exc = APIError(
            "Server error",
            status_code=500,
            response_body='{"error": "Internal server error"}',
            request_id="req-123",
        )
        assert exc.status_code == 500
        assert exc.response_body == '{"error": "Internal server error"}'
        assert exc.request_id == "req-123"
        expected = (
            "Server error | Status: 500 | Request ID: req-123 | "
            'Response: {"error": "Internal server error"}'
        )
        assert str(exc) == expected

    def test_error_string_no_message(self):
        """Test string representation when no message provided."""
        exc = APIError("")
        exc.args = ()  # Simulate no args
        assert str(exc) == "API Error"


class TestValidationError:
    """Test validation error."""

    def test_inheritance(self):
        """Test that ValidationError inherits from NutrientError."""
        assert issubclass(ValidationError, NutrientError)

    def test_basic_error(self):
        """Test basic validation error."""
        exc = ValidationError("Invalid input")
        assert str(exc) == "Invalid input"
        assert exc.errors == {}

    def test_error_with_details(self):
        """Test validation error with field details."""
        errors = {
            "field1": ["Required field"],
            "field2": ["Invalid format"],
        }
        exc = ValidationError("Validation failed", errors=errors)
        assert str(exc) == "Validation failed"
        assert exc.errors == errors


class TestNutrientTimeoutError:
    """Test timeout error."""

    def test_inheritance(self):
        """Test that NutrientTimeoutError inherits from NutrientError."""
        assert issubclass(NutrientTimeoutError, NutrientError)

    def test_instantiation(self):
        """Test basic instantiation."""
        exc = NutrientTimeoutError("Request timed out")
        assert str(exc) == "Request timed out"


class TestFileProcessingError:
    """Test file processing error."""

    def test_inheritance(self):
        """Test that FileProcessingError inherits from NutrientError."""
        assert issubclass(FileProcessingError, NutrientError)

    def test_instantiation(self):
        """Test basic instantiation."""
        exc = FileProcessingError("Failed to process file")
        assert str(exc) == "Failed to process file"
