import pytest
from helpers.api_client import APIClient
from helpers.booking_helpers import (
    create_booking,
    get_booking,
    update_booking_full,
    update_booking_partial,
    delete_booking,
    valid_booking_payload,
)

from helpers.booking_payloads import (
    valid_booking_payload,
    minimal_payload,
    invalid_payload_missing_fields,
    invalid_dates_payload,
)


@pytest.mark.booking
class TestCreateBooking:
    def test_create_booking_success(self):
        client = APIClient()
        booking_id, response = create_booking(client)

        assert response.status_code == 200
        assert booking_id is not None
        assert "booking" in response.json()
        print(response.json())

    def test_create_booking_minimal_payload(self):
        client = APIClient()
        body = minimal_payload()
        booking_id, response = create_booking(client, payload=body)

        assert response.status_code == 200
        assert booking_id is not None
        assert "booking" in response.json()
        data = response.json()["booking"]
        assert data["firstname"] == body["firstname"]
        assert data["lastname"] == body["lastname"]
        print(f"Booking for {data["firstname"]} {data["lastname"]} is done")

    def test_create_booking_with_special_characters(self):
        client = APIClient()
        body = valid_booking_payload()
        body["firstname"] = "Alina-测试-ÄÖÜ"
        body["lastname"] = "O'Connor-测试"
        booking_id, response = create_booking(client, payload=body)

        assert response.status_code == 200
        assert booking_id is not None
        data = response.json()["booking"]
        assert data["firstname"] == body["firstname"]
        assert data["lastname"] == body["lastname"]
        print(f"Booking for {data["firstname"]} {data["lastname"]} is done")


@pytest.mark.getbooking
class TestGetBooking:

    def test_get_booking_by_id(self):
        client = APIClient()
        booking_id, _ = create_booking(client)
        response = get_booking(client, booking_id)

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}")

        data = response.json()
        assert isinstance(data, dict), "Response must be a JSON object"
        assert data.get("firstname"), "Missing 'firstname' field"
        assert data.get("lastname"), "Missing 'lastname' field"
        print(data)

    def test_get_booking_not_found(self):
        client = APIClient()
        non_existent_id = 9999999
        response = get_booking(client, non_existent_id)

        assert response.status_code == 404, (
            f"Expected 404 for non-existing booking, got {response.status_code}")

        assert response.text.strip() == "Not found", (
            f"Unexpected body: {response.text}")

    def test_get_booking_invalid_id_format(self):
        client = APIClient()
        invalid_id = "abc"
        response = get_booking(client, invalid_id)

        assert response.status_code in (400, 404), (
            f"API must not accept invalid ID formats. Got {response.status_code}")








class TestUpdateBooking:
    pass


class TestPartialUpdateBooking:
    pass


class TestDeleteBooking:
    pass



class TestNegativeBooking:
    pass


class TestBoundaryBooking:
    pass
