from playwright.sync_api import Page
from .base_page import BasePage


class BookingPage(BasePage):

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

        self.first_name_input = page.locator("#firstname")
        self.last_name_input = page.locator("#lasttname")
        self.email_input = page.locator("#email")
        self.phone_input = page.locator("#phone")
        self.subject_input = page.locator("#subject")
        self.message_input = page.locator("#description")

        self.submit_button = page.get_by_role("button", name="Reserve Now")
        self.success_banner = page.get_by_role("heading", name="Booking Confirmed")

    def open(self):
        super().open("#booking")

    def fill_booking_form(self, first_name,last_name, email, phone, subject, message):
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.email_input.fill(email)
        self.phone_input.fill(phone)
        # self.subject_input.fill(subject)
        # self.message_input.fill(message)

    def submit(self):
        self.submit_button.click()

    def is_success_message_visible(self) -> bool:
        return self.success_banner.is_visible()
