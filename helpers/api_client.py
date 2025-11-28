import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.config import BASE_URL


class APIClient:

    def __init__(self, token=None):
        self.base_url = BASE_URL
        self.token = token

        # --- Retry Session for stability (important for GitHub Actions) ---
        self.session = requests.Session()

        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
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

    # ---------------------
    #  Request methods
    # ---------------------

    def get(self, endpoint: str, params: dict | None = None):
        url = self.base_url + endpoint
        return self.session.get(url, headers=self._headers(), params=params)

    def post(self, endpoint: str, json: dict | None = None):
        url = self.base_url + endpoint
        return self.session.post(url, headers=self._headers(), json=json)

    def put(self, endpoint: str, json: dict | None = None):
        url = self.base_url + endpoint
        return self.session.put(url, headers=self._headers(), json=json)

    def patch(self, endpoint: str, json: dict | None = None):
        url = self.base_url + endpoint
        return self.session.patch(url, headers=self._headers(), json=json)

    def delete(self, endpoint: str):
        url = self.base_url + endpoint
        return self.session.delete(url, headers=self._headers())
