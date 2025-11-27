from playwright.sync_api import Page


class BasePage:
    """Base class for all Page Objects."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self, path: str = ""):
        """Open page by path relative to base_url."""
        if path:
            url = f"{self.base_url}/{path.strip('/')}"
        else:
            url = self.base_url

        self.page.goto(url)

    def title(self) -> str:
        return self.page.title()

    def has_no_console_errors(self) -> bool:
        console_messages = []
        self.page.on("console", lambda msg: console_messages.append(msg))
        return all("error" not in m.text.lower() for m in console_messages)
