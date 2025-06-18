"""Unit tests for file handling utilities."""

import io

import pytest

from nutrient_dws.file_handler import (
    prepare_file_for_upload,
    prepare_file_input,
)


def test_prepare_file_input_bytes():
    """Test handling of bytes input."""
    test_content = b"Test content"
    content, filename = prepare_file_input(test_content)

    assert content == test_content
    assert filename == "document"


def test_prepare_file_input_file_object():
    """Test handling of file-like object."""
    file_obj = io.BytesIO(b"Binary content")
    content, filename = prepare_file_input(file_obj)

    assert content == b"Binary content"
    assert filename == "document"


def test_prepare_file_input_invalid():
    """Test handling of invalid input."""
    with pytest.raises(ValueError, match="Unsupported file input type"):
        prepare_file_input(123)  # type: ignore


def test_prepare_file_for_upload_bytes():
    """Test preparing bytes for upload."""
    test_content = b"Upload content"
    field_name, file_tuple = prepare_file_for_upload(test_content)

    assert field_name == "file"
    filename, content, content_type = file_tuple
    assert filename == "document"
    assert content == test_content
    assert content_type == "application/octet-stream"


def test_prepare_file_for_upload_custom_field():
    """Test custom field name."""
    test_content = b"Content"
    field_name, _ = prepare_file_for_upload(test_content, field_name="custom")

    assert field_name == "custom"
