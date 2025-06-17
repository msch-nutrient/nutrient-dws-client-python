"""Unit tests for BuildAPIWrapper."""

from unittest.mock import Mock, patch

from nutrient.builder import BuildAPIWrapper


class TestBuildAPIWrapper:
    """Test BuildAPIWrapper class."""

    def test_init(self):
        """Test initialization."""
        mock_client = Mock()
        builder = BuildAPIWrapper(mock_client, "test.pdf")

        assert builder._client is mock_client
        assert builder._input_file == "test.pdf"
        assert builder._parts == []
        assert builder._actions == []
        assert builder._output_options == {}

    def test_add_step_simple(self):
        """Test adding a simple step."""
        mock_client = Mock()
        builder = BuildAPIWrapper(mock_client, "test.pdf")

        result = builder.add_step(tool="flatten-annotations")

        assert result is builder  # Returns self for chaining
        assert len(builder._actions) == 1
        assert builder._actions[0] == {"type": "flatten"}

    def test_add_step_with_options(self):
        """Test adding a step with options."""
        mock_client = Mock()
        builder = BuildAPIWrapper(mock_client, "test.pdf")

        builder.add_step(tool="rotate-pages", options={"degrees": 90})

        assert len(builder._actions) == 1
        assert builder._actions[0] == {
            "type": "rotate",
            "rotateBy": 90,
        }

    def test_add_step_rotate_with_page_indexes(self):
        """Test rotate step with page indexes."""
        mock_client = Mock()
        builder = BuildAPIWrapper(mock_client, "test.pdf")

        builder.add_step(
            tool="rotate-pages",
            options={"degrees": 180, "page_indexes": [0, 2, 4]}
        )

        assert builder._actions[0] == {
            "type": "rotate",
            "rotateBy": 180,
            "pageIndexes": [0, 2, 4],
        }

    def test_add_step_ocr(self):
        """Test OCR step."""
        mock_client = Mock()
        builder = BuildAPIWrapper(mock_client, "test.pdf")

        builder.add_step(tool="ocr-pdf", options={"language": "de"})

        assert builder._actions[0] == {
            "type": "ocr",
            "language": "de",
        }

    def test_add_step_watermark_text(self):
        """Test watermark step with text."""
        mock_client = Mock()
        builder = BuildAPIWrapper(mock_client, "test.pdf")

        builder.add_step(
            tool="watermark-pdf",
            options={
                "text": "CONFIDENTIAL",
                "opacity": 0.3,
                "position": "top-right",
            }
        )

        assert builder._actions[0] == {
            "type": "watermark",
            "text": "CONFIDENTIAL",
            "opacity": 0.3,
            "position": "top-right",
        }

    def test_add_step_watermark_image(self):
        """Test watermark step with image."""
        mock_client = Mock()
        builder = BuildAPIWrapper(mock_client, "test.pdf")

        builder.add_step(
            tool="watermark-pdf",
            options={"image_url": "https://example.com/logo.png"}
        )

        assert builder._actions[0] == {
            "type": "watermark",
            "image": {"url": "https://example.com/logo.png"},
        }

    def test_add_step_unknown_tool(self):
        """Test adding unknown tool passes through."""
        mock_client = Mock()
        builder = BuildAPIWrapper(mock_client, "test.pdf")

        builder.add_step(tool="custom-tool", options={"param": "value"})

        assert builder._actions[0] == {
            "type": "custom-tool",
            "param": "value",
        }

    def test_chaining_multiple_steps(self):
        """Test chaining multiple steps."""
        mock_client = Mock()
        builder = BuildAPIWrapper(mock_client, "test.pdf")

        builder.add_step(tool="rotate-pages", options={"degrees": 90}) \
               .add_step(tool="ocr-pdf") \
               .add_step(tool="watermark-pdf", options={"text": "DRAFT"})

        assert len(builder._actions) == 3
        assert builder._actions[0]["type"] == "rotate"
        assert builder._actions[1]["type"] == "ocr"
        assert builder._actions[2]["type"] == "watermark"

    def test_set_output_options(self):
        """Test setting output options."""
        mock_client = Mock()
        builder = BuildAPIWrapper(mock_client, "test.pdf")

        result = builder.set_output_options(
            metadata={"title": "My Doc", "author": "John"},
            optimize=True,
        )

        assert result is builder  # Returns self for chaining
        assert builder._output_options == {
            "metadata": {"title": "My Doc", "author": "John"},
            "optimize": True,
        }

    def test_build_instructions_simple(self):
        """Test building instructions with minimal setup."""
        mock_client = Mock()
        builder = BuildAPIWrapper(mock_client, "test.pdf")
        builder.add_step(tool="flatten-annotations")

        instructions = builder._build_instructions()

        assert instructions == {
            "parts": [{"file": "file"}],
            "actions": [{"type": "flatten"}],
        }

    def test_build_instructions_with_output_options(self):
        """Test building instructions with output options."""
        mock_client = Mock()
        builder = BuildAPIWrapper(mock_client, "test.pdf")
        builder.add_step(tool="ocr-pdf")
        builder.set_output_options(optimize=True)

        instructions = builder._build_instructions()

        assert instructions == {
            "parts": [{"file": "file"}],
            "actions": [{"type": "ocr"}],
            "output": {"optimize": True},
        }

    def test_execute_no_output_path(self):
        """Test execute without output path."""
        mock_client = Mock()
        mock_client._http_client.post.return_value = b"PDF content"

        builder = BuildAPIWrapper(mock_client, "test.pdf")
        builder.add_step(tool="rotate-pages", options={"degrees": 90})

        with patch("nutrient.builder.prepare_file_for_upload") as mock_prepare:
            mock_prepare.return_value = ("file", ("test.pdf", b"content", "application/pdf"))

            result = builder.execute()

        assert result == b"PDF content"
        mock_client._http_client.post.assert_called_once()

        # Check the call arguments
        call_args = mock_client._http_client.post.call_args
        assert call_args[0][0] == "/build"
        assert "files" in call_args[1]
        assert "json_data" in call_args[1]
        assert call_args[1]["json_data"]["actions"][0]["type"] == "rotate"

    def test_execute_with_output_path(self, tmp_path):
        """Test execute with output path."""
        mock_client = Mock()
        mock_client._http_client.post.return_value = b"PDF content"
        output_file = tmp_path / "output.pdf"

        builder = BuildAPIWrapper(mock_client, "test.pdf")
        builder.add_step(tool="ocr-pdf")

        with patch("nutrient.builder.prepare_file_for_upload") as mock_prepare:
            mock_prepare.return_value = ("file", ("test.pdf", b"content", "application/pdf"))

            result = builder.execute(output_path=str(output_file))

        assert result is None
        assert output_file.exists()
        assert output_file.read_bytes() == b"PDF content"

    def test_str_representation(self):
        """Test string representation."""
        mock_client = Mock()
        builder = BuildAPIWrapper(mock_client, "test.pdf")
        builder.add_step(tool="rotate-pages", options={"degrees": 90})
        builder.add_step(tool="ocr-pdf")

        assert str(builder) == "BuildAPIWrapper(steps=['rotate', 'ocr'])"

    def test_repr_representation(self):
        """Test detailed representation."""
        mock_client = Mock()
        builder = BuildAPIWrapper(mock_client, "test.pdf")
        builder.add_step(tool="rotate-pages", options={"degrees": 90})

        repr_str = repr(builder)
        assert "BuildAPIWrapper(" in repr_str
        assert "input_file='test.pdf'" in repr_str
        assert "actions=[{'type': 'rotate', 'rotateBy': 90}]" in repr_str
