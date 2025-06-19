"""Unit tests for Direct API methods."""

from unittest.mock import MagicMock

import pytest

from nutrient_dws.client import NutrientClient


@pytest.fixture
def mock_client():
    """Create a mock NutrientClient for testing."""
    client = NutrientClient(api_key="test-key")
    client._process_file = MagicMock(return_value=b"mock-result")
    return client


def test_split_pdf_basic(mock_client):
    """Test basic split_pdf functionality."""
    result = mock_client.split_pdf("test.pdf")

    # Verify _process_file was called with correct parameters
    mock_client._process_file.assert_called_once_with(
        "split-pdf", "test.pdf", None, split_type="pages"
    )
    assert result == b"mock-result"


def test_split_pdf_with_page_ranges(mock_client):
    """Test split_pdf with page ranges."""
    page_ranges = ["1-3", "4-6", "7-10"]
    result = mock_client.split_pdf("test.pdf", page_ranges=page_ranges, split_type="pages")

    # Verify _process_file was called with correct parameters
    mock_client._process_file.assert_called_once_with(
        "split-pdf", "test.pdf", None, split_type="pages", page_ranges=page_ranges
    )
    assert result == b"mock-result"


def test_split_pdf_with_output_path(mock_client):
    """Test split_pdf with output path."""
    mock_client._process_file.return_value = None

    result = mock_client.split_pdf("test.pdf", output_path="output.pdf", split_type="bookmarks")

    # Verify _process_file was called with correct parameters
    mock_client._process_file.assert_called_once_with(
        "split-pdf", "test.pdf", "output.pdf", split_type="bookmarks"
    )
    assert result is None


def test_split_pdf_with_all_parameters(mock_client):
    """Test split_pdf with all parameters."""
    page_ranges = ["1-5", "6-10"]
    mock_client.split_pdf(
        "test.pdf", output_path="split_output.pdf", page_ranges=page_ranges, split_type="pages"
    )

    # Verify _process_file was called with correct parameters
    mock_client._process_file.assert_called_once_with(
        "split-pdf", "test.pdf", "split_output.pdf", split_type="pages", page_ranges=page_ranges
    )


def test_split_pdf_bytes_input(mock_client):
    """Test split_pdf with bytes input."""
    pdf_bytes = b"mock-pdf-content"
    result = mock_client.split_pdf(pdf_bytes, page_ranges=["1-2", "3-4"])

    # Verify _process_file was called with correct parameters
    mock_client._process_file.assert_called_once_with(
        "split-pdf", pdf_bytes, None, split_type="pages", page_ranges=["1-2", "3-4"]
    )
    assert result == b"mock-result"
