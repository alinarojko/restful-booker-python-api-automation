from playwright.sync_api import Page
from .base_page import BasePage


class HomePage(BasePage):
    """Page Object for the main 'Shady Meadows B&B' home page."""

    MAIN_HEADING_NAME = "Welcome to Shady Meadows B&B"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

        # restrict to top navigation bar only
        navbar = page.locator("#navbarNav")

        self.nav_rooms = navbar.get_by_role("link", name="Rooms")
        self.nav_booking = navbar.get_by_role("link", name="Booking")
        self.nav_amenities = navbar.get_by_role("link", name="Amenities")
        self.nav_location = navbar.get_by_role("link", name="Location")
        self.nav_contact = navbar.get_by_role("link", name="Contact")
        self.nav_admin = navbar.get_by_role("link", name="Admin")

    def open(self):
        super().open()

    def is_loaded(self) -> bool:
        heading = self.page.get_by_role("heading", name=self.MAIN_HEADING_NAME)
        return heading.is_visible()

    def go_to_rooms(self):
        self.nav_rooms.click()

    def go_to_booking(self):
        self.nav_booking.click()

    def go_to_contact(self):
        self.nav_contact.click()

    def go_to_admin(self):
        self.nav_admin.click()
