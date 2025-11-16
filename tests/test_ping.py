from helpers.api_client import APIClient


def test_ping_liveness_check():
    client = APIClient()
    response = client.get("/ping")

    assert response.status_code == 201, (
        f"Expected status 201, got {response.status_code}, "
        f"body : {response.text}"
    )

    assert response.text is not None, "Response body is None"

    content_type = response.headers.get("Content-Type", "")
    assert "text/plain" in content_type, (
        f"Wrong Content-Type: {content_type}"
    )

    assert response.elapsed.total_seconds() < 2, (
        f"Ping took too long: {response.elapsed.total_seconds()} seconds"
    )

    assert "<html>" not in response.text.lower(), (
        f"Server returned HTML instead of plain text: {response.text}"
    )
