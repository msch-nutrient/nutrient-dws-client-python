"""Configuration for integration tests."""

import pytest


def pytest_configure(config):
    """Add custom markers for integration tests."""
    # Marker is already defined in pyproject.toml
    pass


def pytest_collection_modifyitems(config, items):
    """Automatically mark all tests in integration directory."""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


def pytest_runtest_setup(item):
    """Skip integration tests if running only unit tests."""
    if "integration" in item.keywords and item.config.getoption("--unit-only"):
        pytest.skip("Skipping integration test in unit-only mode")


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--unit-only",
        action="store_true",
        default=False,
        help="Run only unit tests, skip integration tests",
    )
    parser.addoption(
        "--integration-only",
        action="store_true",
        default=False,
        help="Run only integration tests, skip unit tests",
    )
