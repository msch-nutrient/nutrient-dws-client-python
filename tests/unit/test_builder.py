"""Unit tests for BuildAPIWrapper."""

from unittest.mock import Mock

from nutrient_dws.builder import BuildAPIWrapper


def test_builder_init():
    """Test builder initialization."""
    mock_client = Mock()
    builder = BuildAPIWrapper(client=mock_client, input_file="test.pdf")

    assert builder._client == mock_client
    assert builder._input_file == "test.pdf"
    assert builder._actions == []


def test_builder_add_step():
    """Test adding a step."""
    mock_client = Mock()
    builder = BuildAPIWrapper(client=mock_client, input_file="test.pdf")

    result = builder.add_step("convert-to-pdf")

    assert result == builder  # Should return self for chaining
    assert len(builder._actions) == 1
    assert builder._actions[0]["type"] == "convert-to-pdf"


def test_builder_chaining():
    """Test method chaining."""
    mock_client = Mock()
    builder = BuildAPIWrapper(client=mock_client, input_file="test.pdf")

    builder.add_step("convert-to-pdf").add_step("ocr-pdf", {"language": "en"})

    assert len(builder._actions) == 2
    assert builder._actions[0]["type"] == "convert-to-pdf"
    assert builder._actions[1]["type"] == "ocr"


def test_builder_output_options():
    """Test setting output options."""
    mock_client = Mock()
    builder = BuildAPIWrapper(client=mock_client, input_file="test.pdf")

    result = builder.set_output_options(format="pdf")

    assert result == builder
    assert builder._output_options == {"format": "pdf"}


def test_builder_str():
    """Test string representation."""
    mock_client = Mock()
    builder = BuildAPIWrapper(client=mock_client, input_file="test.pdf")
    builder.add_step("convert-to-pdf")

    str_repr = str(builder)
    assert "BuildAPIWrapper" in str_repr
    assert "convert-to-pdf" in str_repr
