"""File handling utilities for input/output operations."""

import io
from pathlib import Path
from typing import BinaryIO, Union

FileInput = Union[str, bytes, BinaryIO]


def prepare_file_input(file_input: FileInput) -> tuple[bytes, str]:
    """Convert various file input types to bytes.

    Args:
        file_input: File path, bytes, or file-like object.

    Returns:
        Tuple of (file_bytes, filename).

    Raises:
        FileNotFoundError: If file path doesn't exist.
        ValueError: If input type is not supported.
    """
    if isinstance(file_input, str):
        path = Path(file_input)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_input}")
        return path.read_bytes(), path.name
    elif isinstance(file_input, bytes):
        return file_input, "document"
    elif isinstance(file_input, io.IOBase):
        content = file_input.read()
        if isinstance(content, str):
            content = content.encode()
        filename = getattr(file_input, "name", "document")
        return content, filename
    else:
        raise ValueError(f"Unsupported file input type: {type(file_input)}")


def save_file_output(content: bytes, output_path: str) -> None:
    """Save file content to disk.

    Args:
        content: File bytes to save.
        output_path: Path where to save the file.
    """
    Path(output_path).write_bytes(content)