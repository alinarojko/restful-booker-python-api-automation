import pytest

@pytest.mark.security
class TestSecurityBasics:

    def test_disallow_put_on_ping(self, client):
        # REST rule: read-only endpoints (/ping) must NOT allow unsafe HTTP methods.
        # Expected: 405 Method Not Allowed or 404.

        response = client.put("/ping", json={"x": 1})

        assert response.status_code in (404, 405), (
            f"Unsafe PUT unexpectedly allowed on /ping: {response.status_code}")

    def test_disallow_delete_on_ping(self, client):
        # REST rule: DELETE on /ping must be disabled.

        response = client.delete("/ping")

        assert response.status_code in (404, 405), (
            f"DELETE unexpectedly allowed on /ping: {response.status_code}")

    def test_content_type_header_present(self, client):
        # REST compliance: API must always return Content-Type.

        response = client.get("/ping")

        assert "Content-Type" in response.headers, "Missing Content-Type header"
        assert response.headers["Content-Type"] != "", "Empty Content-Type value"

    def test_server_header_present(self, client):
        # Good REST hygiene: server must identify itself with a Server header.
        # RESTful Booker returns 'Cowboy', which is expected

        response = client.get("/ping")

        assert "Server" in response.headers, "Missing Server header"
        assert response.headers["Server"], "Server header is empty"

    def test_no_sensitive_headers(self, client):
        # Security rule: API must not leak sensitive server information.
        # We validate ONLY the headers that should NOT be present.

        response = client.get("/ping")
        forbidden_headers = [
            "X-AspNet-Version",
            "X-Generator",
            "X-Drupal-Cache",
            "X-Runtime",]

        for header in forbidden_headers:
            assert header not in response.headers, (
                f"Sensitive header leaked: {header}")
