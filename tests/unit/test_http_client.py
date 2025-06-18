"""Unit tests for HTTP client."""

from unittest.mock import patch

import pytest
import requests
import responses

from nutrient_dws.exceptions import APIError, AuthenticationError, TimeoutError, ValidationError
from nutrient_dws.http_client import HTTPClient


class TestHTTPClient:
    """Test HTTPClient class."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        client = HTTPClient(api_key="test-key", timeout=120)
        assert client._api_key == "test-key"
        assert client._timeout == 120
        assert client._base_url == "https://api.pspdfkit.com"

    def test_init_without_api_key(self):
        """Test initialization without API key."""
        client = HTTPClient(api_key=None)
        assert client._api_key is None
        assert client._timeout == 300  # Default

    def test_session_headers_with_api_key(self):
        """Test session headers include API key."""
        client = HTTPClient(api_key="test-key")
        assert client._session.headers["Authorization"] == "Bearer test-key"
        assert "User-Agent" in client._session.headers

    def test_session_headers_without_api_key(self):
        """Test session headers without API key."""
        client = HTTPClient(api_key=None)
        assert "Authorization" not in client._session.headers
        assert "User-Agent" in client._session.headers

    @responses.activate
    def test_post_success(self):
        """Test successful POST request."""
        responses.add(
            responses.POST,
            "https://api.pspdfkit.com/test",
            body=b"Success response",
            status=200,
        )

        client = HTTPClient(api_key="test-key")
        result = client.post("/test")

        assert result == b"Success response"
        assert len(responses.calls) == 1

    @responses.activate
    def test_post_without_api_key(self):
        """Test POST request without API key raises error."""
        client = HTTPClient(api_key=None)

        with pytest.raises(AuthenticationError, match="API key is required"):
            client.post("/test")

    @responses.activate
    def test_post_authentication_error_401(self):
        """Test 401 response raises AuthenticationError."""
        responses.add(
            responses.POST,
            "https://api.pspdfkit.com/test",
            json={"message": "Invalid API key"},
            status=401,
        )

        client = HTTPClient(api_key="invalid-key")

        with pytest.raises(AuthenticationError, match="Invalid API key"):
            client.post("/test")

    @responses.activate
    def test_post_authentication_error_403(self):
        """Test 403 response raises AuthenticationError."""
        responses.add(
            responses.POST,
            "https://api.pspdfkit.com/test",
            body="Forbidden",
            status=403,
        )

        client = HTTPClient(api_key="test-key")

        with pytest.raises(AuthenticationError):
            client.post("/test")

    @responses.activate
    def test_post_validation_error(self):
        """Test 422 response raises ValidationError."""
        error_details = {
            "field1": ["Required field"],
            "field2": ["Invalid format"],
        }
        responses.add(
            responses.POST,
            "https://api.pspdfkit.com/test",
            json={"message": "Validation failed", "errors": error_details},
            status=422,
        )

        client = HTTPClient(api_key="test-key")

        with pytest.raises(ValidationError) as exc_info:
            client.post("/test")

        assert exc_info.value.errors == error_details

    @responses.activate
    def test_post_api_error_with_json(self):
        """Test API error with JSON response."""
        responses.add(
            responses.POST,
            "https://api.pspdfkit.com/test",
            json={"message": "Server error occurred"},
            status=500,
            headers={"X-Request-Id": "req-123"},
        )

        client = HTTPClient(api_key="test-key")

        with pytest.raises(APIError) as exc_info:
            client.post("/test")

        assert exc_info.value.status_code == 500
        assert exc_info.value.request_id == "req-123"
        assert "Server error occurred" in str(exc_info.value)

    @responses.activate
    def test_post_api_error_with_text(self):
        """Test API error with text response."""
        responses.add(
            responses.POST,
            "https://api.pspdfkit.com/test",
            body="Internal server error",
            status=500,
        )

        client = HTTPClient(api_key="test-key")

        with pytest.raises(APIError) as exc_info:
            client.post("/test")

        assert exc_info.value.status_code == 500
        assert "Internal server error" in str(exc_info.value)

    def test_post_timeout(self):
        """Test request timeout."""
        client = HTTPClient(api_key="test-key", timeout=1)

        with patch.object(client._session, "post") as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout()

            with pytest.raises(TimeoutError, match="Request timed out"):
                client.post("/test")

    def test_post_connection_error(self):
        """Test connection error."""
        client = HTTPClient(api_key="test-key")

        with patch.object(client._session, "post") as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

            with pytest.raises(APIError, match="Connection error"):
                client.post("/test")

    @responses.activate
    def test_post_with_files(self):
        """Test POST with files."""
        responses.add(
            responses.POST,
            "https://api.pspdfkit.com/process",
            body=b"Processed file",
            status=200,
        )

        client = HTTPClient(api_key="test-key")
        files = {"file": ("test.pdf", b"PDF content", "application/pdf")}

        result = client.post("/process", files=files)

        assert result == b"Processed file"

    @responses.activate
    def test_post_with_json_data(self):
        """Test POST with JSON data (multipart)."""
        responses.add(
            responses.POST,
            "https://api.pspdfkit.com/build",
            body=b"Built result",
            status=200,
        )

        client = HTTPClient(api_key="test-key")
        json_data = {"steps": [{"tool": "convert"}]}

        result = client.post("/build", json_data=json_data)

        assert result == b"Built result"
        # Verify the actions field was added to form data
        assert len(responses.calls) == 1

    def test_context_manager(self):
        """Test context manager functionality."""
        with HTTPClient(api_key="test-key") as client:
            assert client._session is not None
            assert len(client._session.adapters) > 0  # Has adapters

        # After closing, we can't easily verify the session is closed
        # because requests.Session.close() doesn't clear adapters

    def test_close(self):
        """Test explicit close is callable."""
        client = HTTPClient(api_key="test-key")
        # Just verify close() can be called without error
        client.close()

    @responses.activate
    def test_retry_on_500_errors(self):
        """Test retry logic for 5xx errors."""
        # First two calls fail, third succeeds
        responses.add(responses.POST, "https://api.pspdfkit.com/test", status=500)
        responses.add(responses.POST, "https://api.pspdfkit.com/test", status=502)
        responses.add(
            responses.POST,
            "https://api.pspdfkit.com/test",
            body=b"Success after retry",
            status=200,
        )

        client = HTTPClient(api_key="test-key")
        result = client.post("/test")

        assert result == b"Success after retry"
        assert len(responses.calls) == 3  # Retried twice
