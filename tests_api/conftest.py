import pytest
from helpers.api_client import APIClient


@pytest.fixture
def client():
    # Basic unauthenticated API client.
    return APIClient()


@pytest.fixture
def auth_token():
    # Generates a valid authorization token for endpoints requiring auth.
    temp = APIClient()
    payload = {"username": "admin", "password": "password123"}
    response = temp.post("/auth", json=payload)

    token = response.json().get("token")
    assert token, "Auth token was not generated"

    return token


@pytest.fixture
def auth_client(auth_token):
    # Authenticated client that includes the token automatically.
    return APIClient(token=auth_token)
