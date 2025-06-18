"""Unit tests for BuildAPIWrapper."""

from unittest.mock import Mock, patch

from nutrient_dws.builder import BuildAPIWrapper


class TestBuildAPIWrapper:
    """Test BuildAPIWrapper class."""

    def test_init(self):
        """Test initialization."""
        mock_client = Mock()
        builder = BuildAPIWrapper(client=mock_client, input_file="test.pdf")

        assert builder._client == mock_client
        assert builder._input_file == "test.pdf"
        assert builder._actions == []
        assert builder._output_options == {}
        assert builder._parts == [{"file": "file"}]
        assert "file" in builder._files

    def test_add_step_basic(self):
        """Test adding a basic step."""
        mock_client = Mock()
        builder = BuildAPIWrapper(client=mock_client, input_file="test.pdf")

        result = builder.add_step("convert-to-pdf")

        assert result == builder  # Should return self for chaining
        assert len(builder._actions) == 1
        assert builder._actions[0]["type"] == "convert-to-pdf"

    def test_add_step_with_options(self):
        """Test adding a step with options."""
        mock_client = Mock()
        builder = BuildAPIWrapper(client=mock_client, input_file="test.pdf")

        builder.add_step("rotate-pages", {"degrees": 90})

        assert len(builder._actions) == 1
        assert builder._actions[0]["type"] == "rotate"
        assert builder._actions[0]["rotateBy"] == 90

    def test_chaining_steps(self):
        """Test chaining multiple steps."""
        mock_client = Mock()
        builder = BuildAPIWrapper(client=mock_client, input_file="test.pdf")

        builder.add_step("convert-to-pdf").add_step("ocr-pdf", {"language": "en"})

        assert len(builder._actions) == 2
        assert builder._actions[0]["type"] == "convert-to-pdf"
        assert builder._actions[1]["type"] == "ocr"
        assert builder._actions[1]["language"] == "english"

    def test_set_output_options(self):
        """Test setting output options."""
        mock_client = Mock()
        builder = BuildAPIWrapper(client=mock_client, input_file="test.pdf")

        result = builder.set_output_options(format="pdf", quality=90)

        assert result == builder  # Should return self for chaining
        assert builder._output_options == {"format": "pdf", "quality": 90}

    def test_build_instructions(self):
        """Test building instructions."""
        mock_client = Mock()
        builder = BuildAPIWrapper(client=mock_client, input_file="test.pdf")

        builder.add_step("convert-to-pdf")
        builder.add_step("ocr-pdf", {"language": "en"})
        builder.set_output_options(format="pdf")

        instructions = builder._build_instructions()

        assert "parts" in instructions
        assert instructions["actions"] == builder._actions
        assert instructions["output"] == {"format": "pdf"}

    def test_execute_returns_bytes(self):
        """Test execute returns bytes when no output path."""
        mock_client = Mock()
        mock_http_client = Mock()
        mock_client._http_client = mock_http_client

        # Mock the response
        mock_response = b"PDF content"
        mock_http_client.post.return_value = mock_response

        builder = BuildAPIWrapper(client=mock_client, input_file=b"input content")
        builder.add_step("convert-to-pdf")

        with patch("nutrient_dws.builder.prepare_file_for_upload") as mock_prepare:
            mock_prepare.return_value = ("file", ("doc.pdf", b"input content", "application/pdf"))

            result = builder.execute()

        assert result == b"PDF content"

    def test_execute_saves_to_file(self):
        """Test execute saves to file when output path provided."""
        mock_client = Mock()
        mock_http_client = Mock()
        mock_client._http_client = mock_http_client

        # Mock the response
        mock_response = b"PDF content"
        mock_http_client.post.return_value = mock_response

        builder = BuildAPIWrapper(client=mock_client, input_file=b"input content")
        builder.add_step("convert-to-pdf")

        with patch("nutrient_dws.builder.prepare_file_for_upload") as mock_prepare:
            mock_prepare.return_value = ("file", ("doc.pdf", b"input content", "application/pdf"))

            with patch("nutrient_dws.builder.save_file_output") as mock_save:
                result = builder.execute("output.pdf")

        assert result is None
        mock_save.assert_called_once_with(b"PDF content", "output.pdf")

    def test_str_representation(self):
        """Test string representation."""
        mock_client = Mock()
        builder = BuildAPIWrapper(client=mock_client, input_file="test.pdf")
        builder.add_step("convert-to-pdf")

        str_repr = str(builder)
        assert "BuildAPIWrapper" in str_repr
        assert "convert-to-pdf" in str_repr

    def test_repr_representation(self):
        """Test repr representation."""
        mock_client = Mock()
        builder = BuildAPIWrapper(client=mock_client, input_file="test.pdf")
        builder.add_step("convert-to-pdf")
        builder.add_step("ocr-pdf")

        repr_str = repr(builder)
        assert "BuildAPIWrapper" in repr_str
        assert "input_file=" in repr_str
        assert "actions=" in repr_str
