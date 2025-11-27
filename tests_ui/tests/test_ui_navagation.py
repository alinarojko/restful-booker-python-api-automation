import pytest
from tests_ui.pages.home_page import HomePage


@pytest.mark.ui
def test_nav_open_rooms_page(page, base_url):
    home = HomePage(page, base_url)
    home.open()

    start_url = page.url
    home.go_to_rooms()

    assert "#rooms" in page.url.lower(), f"Expected #rooms in URL, got: {page.url}"
    assert page.url != start_url, "URL did not change after clicking Rooms"

    assert page.locator("#rooms").first.is_visible(), "Rooms section is not visible"
    assert home.has_no_console_errors(), "Console errors detected on Rooms section"


@pytest.mark.ui
def test_nav_open_booking_page(page, base_url):
    home = HomePage(page, base_url)
    home.open()

    home.go_to_booking()

    assert "#booking" in page.url.lower(), f"Expected #booking in URL, got: {page.url}"
    assert page.locator("#booking").first.is_visible(), "Booking section is not visible"


@pytest.mark.ui
def test_nav_open_contact_page(page, base_url):
    home = HomePage(page, base_url)
    home.open()

    home.go_to_contact()

    assert "#contact" in page.url.lower(), f"Expected #contact in URL, got: {page.url}"
    assert page.locator("#contact").first.is_visible(), "Contact section is not visible"


