from playwright.sync_api import Page
from .base_page import BasePage


class HomePage(BasePage):
    """Page Object for the main 'Shady Meadows B&B' home page."""

    MAIN_HEADING_NAME = "Welcome to Shady Meadows B&B"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    def open(self):
        """Open the home page (base URL)."""
        super().open()

    def is_loaded(self) -> bool:
        """Check that main heading is visible = page loaded correctly."""
        heading = self.page.get_by_role("heading", name=self.MAIN_HEADING_NAME)
        return heading.is_visible()
