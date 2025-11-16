import requests
from config.config import BASE_URL


class APIClient:

    def __init__(self, token=None):
        self.base_url = BASE_URL
        self.token = token

    def _headers(self) -> dict:
        headers = {
            "Content-Type": "application/json"
        }

        if self.token:
            headers["Cookie"] = f"token={self.token}"
        return headers

    def get(self, endpoint: str, params: dict | None = None):
        url = self.base_url + endpoint
        return requests.get(url, headers=self._headers(), params=params)

    def post(self, endpoint: str, json: dict | None = None):
        url = self.base_url + endpoint
        return requests.post(url, headers=self._headers(), json=json)

    def put(self, endpoint: str, json: dict | None = None):
        url = self.base_url + endpoint
        return requests.put(url, headers=self._headers(), json=json)

    def patch(self, endpoint: str, json: dict | None = None):
        url = self.base_url + endpoint
        return requests.patch(url, headers=self._headers(), json=json)

    def delete(self, endpoint: str):
        url = self.base_url + endpoint
        return requests.delete(url, headers=self._headers())
