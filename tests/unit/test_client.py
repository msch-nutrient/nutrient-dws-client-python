"""Unit tests for NutrientClient."""

import os

from nutrient_dws.client import NutrientClient


def test_client_init_with_api_key():
    """Test client initialization with API key."""
    client = NutrientClient(api_key="test-key")
    assert client is not None
    assert client._http_client._api_key == "test-key"


def test_client_init_with_env_var():
    """Test client initialization with environment variable."""
    # Save original value
    original = os.environ.get("NUTRIENT_API_KEY")

    try:
        os.environ["NUTRIENT_API_KEY"] = "env-key"
        client = NutrientClient()
        assert client._http_client._api_key == "env-key"
    finally:
        # Restore original value
        if original is not None:
            os.environ["NUTRIENT_API_KEY"] = original
        else:
            os.environ.pop("NUTRIENT_API_KEY", None)


def test_client_init_precedence():
    """Test that explicit API key takes precedence over env var."""
    # Save original value
    original = os.environ.get("NUTRIENT_API_KEY")

    try:
        os.environ["NUTRIENT_API_KEY"] = "env-key"
        client = NutrientClient(api_key="explicit-key")
        assert client._http_client._api_key == "explicit-key"
    finally:
        # Restore original value
        if original is not None:
            os.environ["NUTRIENT_API_KEY"] = original
        else:
            os.environ.pop("NUTRIENT_API_KEY", None)


def test_client_build_method():
    """Test that build() returns a BuildAPIWrapper."""
    client = NutrientClient(api_key="test-key")
    builder = client.build("test.pdf")

    # Check class name to avoid import issues
    assert builder.__class__.__name__ == "BuildAPIWrapper"


def test_client_has_direct_api_methods():
    """Test that client has direct API methods."""
    client = NutrientClient(api_key="test-key")

    # Check that direct API methods exist (from DirectAPIMixin)
    assert hasattr(client, "convert_to_pdf")
    assert hasattr(client, "flatten_annotations")
    assert hasattr(client, "rotate_pages")
    assert hasattr(client, "watermark_pdf")
    assert hasattr(client, "ocr_pdf")
    assert hasattr(client, "apply_redactions")
    assert hasattr(client, "merge_pdfs")
    assert hasattr(client, "split_pdf")
    assert hasattr(client, "duplicate_pdf_pages")
    assert hasattr(client, "delete_pdf_pages")
    assert hasattr(client, "add_page")


def test_client_context_manager():
    """Test client can be used as context manager."""
    with NutrientClient(api_key="test-key") as client:
        assert client is not None
        # Check that HTTP client is not closed
        assert hasattr(client._http_client, "_session")

    # After exiting context, HTTP client session should be closed
    # We can't directly check if closed, but the method should have been called


def test_client_close():
    """Test client close method."""
    client = NutrientClient(api_key="test-key")

    # Verify HTTP client exists
    assert hasattr(client, "_http_client")

    # Close should not raise an error
    client.close()
