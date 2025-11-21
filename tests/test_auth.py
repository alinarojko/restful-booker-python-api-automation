import pytest


@pytest.mark.auth
class TestAuthBasics:

    @pytest.mark.smoke
    def test_auth_success(self, client):
        payload = {"username": "admin", "password": "password123"}
        response = client.post("/auth", json=payload)
        data = response.json()

        assert response.status_code == 200
        assert "token" in data, f"No token returned: {data}"
        assert data["token"], "Token is empty"

    @pytest.mark.negative
    def test_auth_invalid_password(self, client):
        payload = {"username": "admin", "password": "incorrect_password"}
        response = client.post("/auth", json=payload)
        data = response.json()

        assert response.status_code == 200
        assert data.get("reason") == "Bad credentials"
        assert "token" not in data

    @pytest.mark.negative
    def test_auth_missing_username(self, client):
        payload = {"username": "wrong_username", "password": "password123"}
        response = client.post("/auth", json=payload)
        data = response.json()

        assert response.status_code == 200
        assert data.get("reason") == "Bad credentials"
        assert "token" not in data

    @pytest.mark.negative
    def test_auth_missing_field(self, client):
        payload = {"username": "admin", "password": ""}
        response = client.post("/auth", json=payload)
        data = response.json()

        assert response.status_code == 200
        assert data.get("reason") == "Bad credentials"
        assert "token" not in data

    @pytest.mark.negative
    def test_auth_empty_body(self, client):
        response = client.post("/auth", json={})
        data = response.json()

        assert response.status_code == 200
        assert data.get("reason") == "Bad credentials"
        assert "token" not in data

    @pytest.mark.negative
    def test_auth_non_json_body(self, client):
        response = client.post("/auth", json=None)
        data = response.json()

        assert response.status_code == 200
        assert data.get("reason") == "Bad credentials"
        assert "token" not in data