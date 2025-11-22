from playwright.sync_api import Page


class BasePage:
    """Base class for all Page Objects. """

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rsplit("/")

    def open(self, path: str = ""):
        """Open page by path relative to base_url."""
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        self.page.goto(url)

    def title(self) -> str:
        """Return current page title."""
        return self.page.title()

    def has_no_console_errors(self) -> bool:
        """Collect console messages and check there are no 'error' entries."""
        console_messages = []

        def _handler(msg):
            console_messages.append(msg)

        self.page.on("console", _handler)
        return all("error" not in m.text.lower() for m in console_messages)
