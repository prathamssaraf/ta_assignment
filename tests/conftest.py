"""Pytest configuration and shared fixtures."""

import contextlib

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may be slow)"
    )
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Automatically mark tests based on their location."""
    for item in items:
        # Mark tests in unit/ directory as unit tests
        if "unit" in str(item.fspath) or ("/src/" in str(item.fspath) and "/tests/" in str(item.fspath)):
            item.add_marker(pytest.mark.unit)

        # Mark tests in integration/ directory as integration tests
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark tests in e2e/ directory as e2e tests
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)