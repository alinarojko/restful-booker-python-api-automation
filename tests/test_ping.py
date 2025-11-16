from helpers.api_client import APIClient


def test_ping_basic_liveness():
    """
    Basic smoke test to confirm the service is alive.
    Covers:
    - Correct status code
    - Correct body text
    - Correct Content-Type
    - Fast response time
    - No HTML returned
    """

    client = APIClient()
    response = client.get("/ping")

    # Status must be 201
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"

    # Body must be exactly "Created"
    body = response.text.strip().lower()
    assert body == "created", f"Unexpected body: {response.text}"

    # Content-Type must be plain text
    content_type = response.headers.get("Content-Type", "")
    assert "text/plain" in content_type, f"Wrong Content-Type: {content_type}"

    # Response must be fast
    assert response.elapsed.total_seconds() < 2, (
        f"Ping too slow: {response.elapsed.total_seconds()}s"
    )

    # No HTML allowed
    assert "<html>" not in body, "Server returned HTML instead of plain text"
