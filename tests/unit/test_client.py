"""Unit tests for NutrientClient."""

import os
from unittest.mock import patch

from nutrient_dws import NutrientClient
from nutrient_dws.builder import BuildAPIWrapper


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

            # Mock prepare_file_for_upload to avoid file not found
            with patch("nutrient_dws.builder.prepare_file_for_upload") as mock_prepare:
                mock_prepare.return_value = ("file", ("input.pdf", b"content", "application/pdf"))

                result = client._process_file("test-tool", "input.pdf", degrees=90)

            assert result == b"PDF content"
            mock_post.assert_called_once()

            # Check the call arguments - now uses /build endpoint
            call_args = mock_post.call_args
            assert call_args[0][0] == "/build"

    def test_process_file_with_output_path(self, tmp_path):
        """Test _process_file saves to file when output_path provided."""
        client = NutrientClient(api_key="test-key")
        output_file = tmp_path / "output.pdf"

        with patch.object(client._http_client, "post") as mock_post:
            mock_post.return_value = b"PDF content"

            # Mock prepare_file_for_upload to avoid file not found
            with patch("nutrient_dws.builder.prepare_file_for_upload") as mock_prepare:
                mock_prepare.return_value = ("file", ("input.pdf", b"content", "application/pdf"))

                # Also need to mock save_file_output
                with patch("nutrient_dws.builder.save_file_output") as mock_save:
                    result = client._process_file(
                        "test-tool", "input.pdf", output_path=str(output_file)
                    )

                    # Verify save was called with the right arguments
                    mock_save.assert_called_once_with(b"PDF content", str(output_file))

            assert result is None

    def test_context_manager(self):
        """Test client can be used as context manager."""
        with NutrientClient(api_key="test-key") as client:
            assert client._http_client is not None

        # Verify close was called (can't easily check session state)

    def test_close(self):
        """Test explicit close is callable."""
        client = NutrientClient(api_key="test-key")
        # Just verify close() can be called without error
        client.close()

    def test_convert_to_pdf_integration(self):
        """Test convert_to_pdf method integration."""
        client = NutrientClient(api_key="test-key")

        with patch.object(client._http_client, "post") as mock_post:
            mock_post.return_value = b"PDF content"

            with patch("nutrient_dws.builder.prepare_file_for_upload") as mock_prepare:
                mock_prepare.return_value = (
                    "file",
                    (
                        "document.docx",
                        b"content",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    ),
                )

                result = client.convert_to_pdf("document.docx")

            assert result == b"PDF content"
            mock_post.assert_called_once()
            # Should use /build endpoint with no actions for implicit conversion
            call_args = mock_post.call_args
            assert call_args[0][0] == "/build"

    def test_rotate_pages_integration(self):
        """Test rotate_pages method integration with parameters."""
        client = NutrientClient(api_key="test-key")

        with patch.object(client, "_process_file") as mock_process:
            mock_process.return_value = b"Rotated PDF"

            result = client.rotate_pages("input.pdf", degrees=90, page_indexes=[0, 1, 2])

            mock_process.assert_called_once_with(
                "rotate-pages", "input.pdf", None, degrees=90, page_indexes=[0, 1, 2]
            )
            assert result == b"Rotated PDF"
