"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

# Add workspace packages to path
for package_dir in ["message/src", "mail_client_api/src", "gmail_message_impl/src", "gmail_client_impl/src"]:
    package_path = src_dir / package_dir
    if package_path.exists():
        sys.path.insert(0, str(package_path))

# Import main modules to ensure coverage (with error handling for missing dependencies)
try:
    import mail_client_api  # noqa: F401
except ImportError:
    pass

try:
    import gmail_client_impl  # noqa: F401
except ImportError:
    pass


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
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Mark tests in package src/*/tests/ directories as unit tests
        elif "/src/" in str(item.fspath) and "/tests/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Mark tests in integration/ directory as integration tests
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark tests in e2e/ directory as e2e tests
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
