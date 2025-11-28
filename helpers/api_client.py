import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.config import BASE_URL


class APIClient:

    def __init__(self, token=None):
        self.base_url = BASE_URL
        self.token = token

        # --- Stable retry session for CI ---
        self.session = requests.Session()

        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=False,        # Retry ВСЕ методы, включая POST
            raise_on_status=False,        # НЕ выбрасывать ResponseError
            raise_on_redirect=False       # Избегает RetryError от heroku redirects
        )

        adapter = HTTPAdapter(max_retries=retries)

        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _headers(self) -> dict:
        headers = {
            "Content-Type": "application/json"
        }
        if self.token:
            headers["Cookie"] = f"token={self.token}"
        return headers

    def get(self, endpoint: str, params: dict | None = None):
        return self.session.get(self.base_url + endpoint, headers=self._headers(), params=params)

    def post(self, endpoint: str, json: dict | None = None):
        return self.session.post(self.base_url + endpoint, headers=self._headers(), json=json)

    def put(self, endpoint: str, json: dict | None = None):
        return self.session.put(self.base_url + endpoint, headers=self._headers(), json=json)

    def patch(self, endpoint: str, json: dict | None = None):
        return self.session.patch(self.base_url + endpoint, headers=self._headers(), json=json)

    def delete(self, endpoint: str):
        return self.session.delete(self.base_url + endpoint, headers=self._headers())
