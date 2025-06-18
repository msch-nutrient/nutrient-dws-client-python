"""Test if importing the package works."""


def test_import_client():
    """Test importing NutrientClient."""
    from nutrient_dws.client import NutrientClient
    assert NutrientClient is not None


def test_import_exceptions():
    """Test importing exceptions."""
    from nutrient_dws.exceptions import NutrientError
    assert NutrientError is not None