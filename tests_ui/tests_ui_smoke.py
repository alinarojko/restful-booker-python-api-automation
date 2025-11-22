import pytest
from tests_ui.pages.home_page import HomePage


@pytest.mark.ui
def test_ui_smoke_open_main_page(page, base_url):
    home = HomePage(page, base_url)

    # 1. Open page
    home.open()

    # 2. Title exists
    assert home.title(), "Page title is empty → page did not load"

    # 3. No console errors
    assert home.has_no_console_errors(), "Found console errors in browser console"

    # 4. Main heading visible
    assert home.is_loaded(), "Main heading 'Welcome to Shady Meadows B&B' not visible"
