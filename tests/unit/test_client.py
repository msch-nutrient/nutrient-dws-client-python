"""Unit tests for NutrientClient."""

import os
from unittest.mock import Mock, patch

import pytest

from nutrient import NutrientClient
from nutrient.builder import BuildAPIWrapper
from nutrient.exceptions import AuthenticationError


class TestNutrientClient:
    """Test NutrientClient class."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        client = NutrientClient(api_key="test-key", timeout=120)
        assert client._api_key == "test-key"
        assert client._timeout == 120

    def test_init_with_env_var(self):
        """Test initialization with environment variable."""
        with patch.dict(os.environ, {"NUTRIENT_API_KEY": "env-key"}):
            client = NutrientClient()
            assert client._api_key == "env-key"
            assert client._timeout == 300  # Default

    def test_init_api_key_precedence(self):
        """Test that constructor API key takes precedence over env var."""
        with patch.dict(os.environ, {"NUTRIENT_API_KEY": "env-key"}):
            client = NutrientClient(api_key="param-key")
            assert client._api_key == "param-key"

    def test_build_returns_builder(self):
        """Test that build() returns BuildAPIWrapper."""
        client = NutrientClient(api_key="test-key")
        builder = client.build(input_file="test.pdf")
        
        assert isinstance(builder, BuildAPIWrapper)
        assert builder._client is client
        assert builder._input_file == "test.pdf"

    def test_has_direct_api_methods(self):
        """Test that client has Direct API methods from mixin."""
        client = NutrientClient(api_key="test-key")
        
        # Check for some key methods
        assert hasattr(client, "convert_to_pdf")
        assert hasattr(client, "ocr_pdf")
        assert hasattr(client, "rotate_pages")
        assert hasattr(client, "watermark_pdf")

    def test_process_file_no_output_path(self):
        """Test _process_file returns bytes when no output_path."""
        client = NutrientClient(api_key="test-key")
        
        with patch.object(client._http_client, "post") as mock_post:
            mock_post.return_value = b"PDF content"
            
            result = client._process_file("test-tool", "input.pdf", degrees=90)
            
            assert result == b"PDF content"
            mock_post.assert_called_once()
            
            # Check the call arguments
            call_args = mock_post.call_args
            assert call_args[0][0] == "/process/test-tool"
            assert "degrees" in call_args[1]["data"]
            assert call_args[1]["data"]["degrees"] == "90"

    def test_process_file_with_output_path(self, tmp_path):
        """Test _process_file saves to file when output_path provided."""
        client = NutrientClient(api_key="test-key")
        output_file = tmp_path / "output.pdf"
        
        with patch.object(client._http_client, "post") as mock_post:
            mock_post.return_value = b"PDF content"
            
            result = client._process_file(
                "test-tool",
                "input.pdf",
                output_path=str(output_file)
            )
            
            assert result is None
            assert output_file.exists()
            assert output_file.read_bytes() == b"PDF content"

    def test_context_manager(self):
        """Test client can be used as context manager."""
        with NutrientClient(api_key="test-key") as client:
            assert client._http_client is not None
        
        # HTTP client should be closed
        assert client._http_client._session.adapters == {}

    def test_close(self):
        """Test explicit close."""
        client = NutrientClient(api_key="test-key")
        client.close()
        
        # HTTP client should be closed
        assert client._http_client._session.adapters == {}

    def test_convert_to_pdf_integration(self):
        """Test convert_to_pdf method integration."""
        client = NutrientClient(api_key="test-key")
        
        with patch.object(client, "_process_file") as mock_process:
            mock_process.return_value = b"PDF content"
            
            result = client.convert_to_pdf("document.docx")
            
            mock_process.assert_called_once_with(
                "convert-to-pdf",
                "document.docx",
                None
            )
            assert result == b"PDF content"

    def test_rotate_pages_integration(self):
        """Test rotate_pages method integration with parameters."""
        client = NutrientClient(api_key="test-key")
        
        with patch.object(client, "_process_file") as mock_process:
            mock_process.return_value = b"Rotated PDF"
            
            result = client.rotate_pages(
                "input.pdf",
                degrees=90,
                page_indexes=[0, 1, 2]
            )
            
            mock_process.assert_called_once_with(
                "rotate-pages",
                "input.pdf",
                None,
                degrees=90,
                page_indexes=[0, 1, 2]
            )
            assert result == b"Rotated PDF"