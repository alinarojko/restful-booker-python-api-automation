import pytest


@pytest.fixture(scope="session")
def base_url():
    """Base URL for UI tests."""
    return "https://automationintesting.online/"
