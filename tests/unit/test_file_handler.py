"""Unit tests for file handling utilities."""

import io
from pathlib import Path

import pytest

from nutrient.file_handler import (
    get_file_size,
    prepare_file_for_upload,
    prepare_file_input,
    save_file_output,
    stream_file_content,
)


class TestPrepareFileInput:
    """Test prepare_file_input function."""

    def test_file_path_input(self, tmp_path):
        """Test handling of file path input."""
        # Create test file
        test_file = tmp_path / "test.pdf"
        test_content = b"PDF content"
        test_file.write_bytes(test_content)
        
        content, filename = prepare_file_input(str(test_file))
        
        assert content == test_content
        assert filename == "test.pdf"

    def test_file_path_not_found(self):
        """Test handling of non-existent file path."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            prepare_file_input("/non/existent/file.pdf")

    def test_bytes_input(self):
        """Test handling of bytes input."""
        test_content = b"Raw bytes content"
        
        content, filename = prepare_file_input(test_content)
        
        assert content == test_content
        assert filename == "document"

    def test_file_like_object_binary(self):
        """Test handling of binary file-like object."""
        test_content = b"File-like content"
        file_obj = io.BytesIO(test_content)
        
        content, filename = prepare_file_input(file_obj)
        
        assert content == test_content
        assert filename == "document"

    def test_file_like_object_text(self):
        """Test handling of text file-like object."""
        test_content = "Text content"
        file_obj = io.StringIO(test_content)
        
        content, filename = prepare_file_input(file_obj)
        
        assert content == test_content.encode()
        assert filename == "document"

    def test_file_like_object_with_name(self, tmp_path):
        """Test handling of file-like object with name attribute."""
        test_file = tmp_path / "named.txt"
        test_content = b"Named file content"
        test_file.write_bytes(test_content)
        
        with open(test_file, "rb") as f:
            content, filename = prepare_file_input(f)
        
        assert content == test_content
        assert filename == "named.txt"

    def test_unsupported_input_type(self):
        """Test handling of unsupported input type."""
        with pytest.raises(ValueError, match="Unsupported file input type"):
            prepare_file_input(123)


class TestPrepareFileForUpload:
    """Test prepare_file_for_upload function."""

    def test_small_file_path(self, tmp_path):
        """Test handling of small file path."""
        test_file = tmp_path / "small.pdf"
        test_content = b"Small PDF"
        test_file.write_bytes(test_content)
        
        field_name, file_tuple = prepare_file_for_upload(str(test_file))
        filename, content, content_type = file_tuple
        
        assert field_name == "file"
        assert filename == "small.pdf"
        assert content == test_content
        assert content_type == "application/octet-stream"

    def test_large_file_path(self, tmp_path):
        """Test handling of large file path (returns file handle)."""
        test_file = tmp_path / "large.pdf"
        # Create 11MB file
        test_content = b"X" * (11 * 1024 * 1024)
        test_file.write_bytes(test_content)
        
        field_name, file_tuple = prepare_file_for_upload(str(test_file))
        filename, file_handle, content_type = file_tuple
        
        assert field_name == "file"
        assert filename == "large.pdf"
        assert hasattr(file_handle, "read")
        assert content_type == "application/octet-stream"
        
        # Clean up
        file_handle.close()

    def test_bytes_input(self):
        """Test handling of bytes input."""
        test_content = b"Bytes content"
        
        field_name, file_tuple = prepare_file_for_upload(test_content)
        filename, content, content_type = file_tuple
        
        assert field_name == "file"
        assert filename == "document"
        assert content == test_content
        assert content_type == "application/octet-stream"

    def test_custom_field_name(self):
        """Test custom field name."""
        test_content = b"Content"
        
        field_name, _ = prepare_file_for_upload(test_content, field_name="custom_file")
        
        assert field_name == "custom_file"


class TestSaveFileOutput:
    """Test save_file_output function."""

    def test_save_to_existing_directory(self, tmp_path):
        """Test saving file to existing directory."""
        output_path = tmp_path / "output.pdf"
        content = b"PDF output"
        
        save_file_output(content, str(output_path))
        
        assert output_path.exists()
        assert output_path.read_bytes() == content

    def test_save_creates_parent_directories(self, tmp_path):
        """Test saving file creates parent directories."""
        output_path = tmp_path / "new" / "dir" / "output.pdf"
        content = b"PDF output"
        
        save_file_output(content, str(output_path))
        
        assert output_path.exists()
        assert output_path.read_bytes() == content


class TestStreamFileContent:
    """Test stream_file_content function."""

    def test_stream_file(self, tmp_path):
        """Test streaming file content."""
        test_file = tmp_path / "stream.txt"
        test_content = b"A" * 5000  # 5KB
        test_file.write_bytes(test_content)
        
        chunks = list(stream_file_content(str(test_file), chunk_size=1024))
        
        assert len(chunks) == 5  # 5 chunks of 1KB each
        assert b"".join(chunks) == test_content

    def test_stream_nonexistent_file(self):
        """Test streaming non-existent file."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            list(stream_file_content("/non/existent/file.txt"))


class TestGetFileSize:
    """Test get_file_size function."""

    def test_file_path_size(self, tmp_path):
        """Test getting size of file path."""
        test_file = tmp_path / "sized.bin"
        test_content = b"X" * 1234
        test_file.write_bytes(test_content)
        
        size = get_file_size(str(test_file))
        
        assert size == 1234

    def test_nonexistent_file_size(self):
        """Test getting size of non-existent file."""
        size = get_file_size("/non/existent/file.bin")
        
        assert size is None

    def test_bytes_size(self):
        """Test getting size of bytes."""
        test_content = b"Y" * 567
        
        size = get_file_size(test_content)
        
        assert size == 567

    def test_seekable_file_size(self):
        """Test getting size of seekable file-like object."""
        test_content = b"Z" * 890
        file_obj = io.BytesIO(test_content)
        file_obj.seek(10)  # Move position
        
        size = get_file_size(file_obj)
        
        assert size == 890
        assert file_obj.tell() == 10  # Position restored

    def test_non_seekable_file_size(self):
        """Test getting size of non-seekable object."""
        # Mock a non-seekable object
        class NonSeekable:
            def read(self):
                return b"content"
        
        size = get_file_size(NonSeekable())
        
        assert size is None