"""Unit tests for NutrientClient."""

from nutrient_dws.client import NutrientClient


def test_client_init():
    """Test client initialization."""
    client = NutrientClient(api_key="test-key")
    assert client is not None
