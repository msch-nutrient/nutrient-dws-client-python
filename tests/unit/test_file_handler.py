"""Unit tests for file handling utilities."""

import io
import tempfile
from pathlib import Path

import pytest

from nutrient_dws.file_handler import (
    get_file_size,
    prepare_file_for_upload,
    prepare_file_input,
    save_file_output,
)


class TestPrepareFileInput:
    """Test prepare_file_input function."""

    def test_bytes_input(self):
        """Test handling of bytes input."""
        test_content = b"Test content"
        content, filename = prepare_file_input(test_content)

        assert content == test_content
        assert filename == "document"

    def test_string_path_input(self):
        """Test handling of string path input."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"File content")
            tmp_path = tmp.name

        try:
            content, filename = prepare_file_input(tmp_path)
            assert content == b"File content"
            assert Path(tmp_path).name in filename
        finally:
            Path(tmp_path).unlink()

    def test_path_object_input(self):
        """Test handling of Path object input."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(b"PDF content")
            tmp_path = Path(tmp.name)

        try:
            content, filename = prepare_file_input(tmp_path)
            assert content == b"PDF content"
            assert tmp_path.name == filename
        finally:
            tmp_path.unlink()

    def test_file_not_found(self):
        """Test handling of non-existent file."""
        with pytest.raises(FileNotFoundError):
            prepare_file_input("non_existent_file.pdf")

    def test_file_like_object(self):
        """Test handling of file-like object."""
        file_obj = io.BytesIO(b"Binary content")
        content, filename = prepare_file_input(file_obj)

        assert content == b"Binary content"
        assert filename == "document"

    def test_unsupported_input_type(self):
        """Test handling of unsupported input type."""
        with pytest.raises(ValueError, match="Unsupported file input type"):
            prepare_file_input(123)  # type: ignore


class TestPrepareFileForUpload:
    """Test prepare_file_for_upload function."""

    def test_bytes_upload(self):
        """Test preparing bytes for upload."""
        test_content = b"Upload content"
        field_name, file_tuple = prepare_file_for_upload(test_content)

        assert field_name == "file"
        filename, content, content_type = file_tuple
        assert filename == "document"
        assert content == test_content
        assert content_type == "application/octet-stream"

    def test_custom_field_name(self):
        """Test custom field name."""
        test_content = b"Content"
        field_name, _ = prepare_file_for_upload(test_content, field_name="custom")

        assert field_name == "custom"


class TestSaveFileOutput:
    """Test save_file_output function."""

    def test_save_to_path(self):
        """Test saving content to file."""
        content = b"Save this content"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.pdf"
            save_file_output(content, str(output_path))

            assert output_path.exists()
            assert output_path.read_bytes() == content

    def test_create_parent_directories(self):
        """Test creating parent directories."""
        content = b"Content"

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "sub" / "dir" / "output.pdf"
            save_file_output(content, str(output_path))

            assert output_path.exists()
            assert output_path.read_bytes() == content


class TestGetFileSize:
    """Test get_file_size function."""

    def test_bytes_size(self):
        """Test getting size of bytes."""
        content = b"12345"
        size = get_file_size(content)
        assert size == 5

    def test_file_path_size(self):
        """Test getting size of file path."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"1234567890")
            tmp_path = tmp.name

        try:
            size = get_file_size(tmp_path)
            assert size == 10
        finally:
            Path(tmp_path).unlink()

    def test_non_existent_file_size(self):
        """Test getting size of non-existent file."""
        size = get_file_size("non_existent.pdf")
        assert size is None

    def test_file_object_size(self):
        """Test getting size of file-like object."""
        file_obj = io.BytesIO(b"123")
        size = get_file_size(file_obj)
        assert size == 3
        # Ensure position is restored
        assert file_obj.tell() == 0
