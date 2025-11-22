import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def base_url():
    """Base URL for UI tests."""
    return "https://automationintesting.online/"


@pytest.fixture(scope="session")
def playwright_instance():
    """Start Playwrite for the entire test session."""
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance):
    """Launch a single browser for all tests."""
    browser = playwright_instance.chromium.launch(headless=False)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(context):
    """Create a fresh page for each test."""
    page = context.new_page()
    yield page
    page.close()


