"""Configuration for integration tests."""

import pytest


def pytest_collection_modifyitems(config, items):
    """Automatically mark all tests in integration directory."""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
