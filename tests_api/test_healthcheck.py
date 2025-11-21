from helpers.api_client import APIClient
import pytest


@pytest.mark.healthcheck
def test_health_status_code():
    # Verify that /ping returns the expected 201 status
    response = APIClient().get("/ping")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"


@pytest.mark.healthcheck
def test_health_body_is_correct():
    # Body must not be empty and must equal 'Created'
    response = APIClient().get("/ping")
    body = response.text.strip()

    assert body != "", "Body is empty"
    assert body.lower() == "created", f"Unexpected body: {body}"


@pytest.mark.healthcheck
def test_health_content_type():
    # API must return text/plain
    response = APIClient().get("/ping")
    ct = response.headers.get("Content-Type", "")
    assert "text/plain" in ct, f"Wrong Content-Type: {ct}"


@pytest.mark.healthcheck
def test_health_no_html():
    # Backend must not return HTML
    response = APIClient().get("/ping")
    assert "<html>" not in response.text.lower(), (
        f"HTML detected: {response.text}"
    )


@pytest.mark.healthcheck
def test_health_not_json():
    # API must not return JSON for /ping
    response = APIClient().get("/ping")

    try:
        response.json()
        assert False, "Ping returned JSON instead of plain text"
    except Exception:
        pass  # Expected behavior


@pytest.mark.healthcheck
def test_health_response_time():
    # Ping must respond in under 2 seconds
    response = APIClient().get("/ping")
    assert response.elapsed.total_seconds() < 2, (
        f"Response too slow: {response.elapsed.total_seconds()}s"
    )


@pytest.mark.healthcheck
def test_health_required_headers_present():
    # Check essential headers that indicate a healthy server
    response = APIClient().get("/ping")

    # minimal, realistic set of required headers
    required_headers = ["Server", "Content-Type", "Date"]

    for header in required_headers:
        assert header in response.headers, f"Missing header: {header}"



