import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import pytest

from helpers.booking_helpers import (
    create_booking,
    get_booking,
    update_booking_full,
    update_booking_partial,
    delete_booking,
    valid_booking_payload,)

from helpers.booking_payloads import (
    valid_booking_payload,
    minimal_payload,
    invalid_payload_missing_fields,
    invalid_dates_payload,)


@pytest.mark.createbooking
@pytest.mark.booking
class TestCreateBooking:
    def test_create_booking_success(self, client):
        booking_id, response = create_booking(client)

        assert response.status_code == 200
        assert booking_id is not None
        assert "booking" in response.json()
        print(response.json())

    def test_create_booking_minimal_payload(self, client):
        body = minimal_payload()
        booking_id, response = create_booking(client, payload=body)

        assert response.status_code == 200
        assert booking_id is not None
        assert "booking" in response.json()
        data = response.json()["booking"]
        assert data["firstname"] == body["firstname"]
        assert data["lastname"] == body["lastname"]
        print(f"Booking for {data["firstname"]} {data["lastname"]} is done")

    def test_create_booking_with_special_characters(self, client):
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


@pytest.mark.booking
@pytest.mark.getbooking
class TestGetBookingByID:

    def test_get_booking_by_id(self, client):
        booking_id, _ = create_booking(client)
        response = get_booking(client, booking_id)

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}")

        data = response.json()
        assert isinstance(data, dict), "Response must be a JSON object"
        assert data.get("firstname"), "Missing 'firstname' field"
        assert data.get("lastname"), "Missing 'lastname' field"
        print(data)

    def test_get_booking_not_found(self, client):
        non_existent_id = 9999999
        response = get_booking(client, non_existent_id)

        assert response.status_code == 404, (
            f"Expected 404 for non-existing booking, got {response.status_code}")

    def test_get_booking_invalid_id_format(self, client):
        invalid_id = "abc"
        response = get_booking(client, invalid_id)

        assert response.status_code in (400, 404), (
            f"API must not accept invalid ID formats. Got {response.status_code}")

    def test_get_booking_performance(self, client):
        booking_id, _ = create_booking(client)
        response = get_booking(client, booking_id)
        elapsed = response.elapsed.total_seconds()

        assert elapsed < 1, (
            f"GET /booking/{booking_id} too slow: {elapsed} seconds")

    def test_get_booking_schema_validation(self, client):
        booking_id, _ = create_booking(client)
        response = get_booking(client, booking_id)
        data = response.json()
        schema_path = "../schemas/booking_schema.json"

        with open(schema_path) as f:
            schema = json.load(f)

        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            assert False, f"JSON schema validation failed: {e.message}"


@pytest.mark.booking
@pytest.mark.getbooking
class TestGetBookingFilters:
    def test_get_booking_by_first_name(self, client):
        # Create booking and extract firstname
        booking_id, response = create_booking(client)
        firstname = response.json()["booking"]["firstname"]

        # Get bookings by firstname
        response = client.get("/booking", params={"firstname": firstname})
        assert response.status_code == 200

        # Response = list of {"bookingid": X}
        returned_ids = [item["bookingid"] for item in response.json()]

        # Validate
        assert booking_id in returned_ids, (
            f"Booking ID {booking_id} not found in filtered results {returned_ids}")

    def test_get_booking_fullname(self, client):
        booking_id, response = create_booking(client)

        first_name = response.json()["booking"]["firstname"]
        last_name = response.json()["booking"]["lastname"]
        response = client.get("/booking", params={
            "firstname": first_name,
            "lastname": last_name})

        assert response.status_code == 200, (
                f"Expected 200, got {response.status_code}")

        returned_ids = [item["bookingid"] for item in response.json()]

        # Validate that our ID is present
        assert booking_id in returned_ids, (
            f"Booking {booking_id} not found in results: {returned_ids}")

    def test_filters_no_result(self, client):
        response = client.get("/booking", params={"firstname": "____NotValidName_____"})
        assert response.status_code == 200
        assert response.json() == [], "Expected empty list for non-existing name"

    def test_filter_by_multiple_params(self, client):
        booking_id, response = create_booking(client)
        body = response.json()["booking"]

        firstname = body["firstname"]
        last_name = body["lastname"]

        resp = client.get("/booking", params={"firstname": firstname, "last_name": last_name})
        assert resp.status_code == 200

        ids = [item["bookingid"] for item in resp.json()]
        assert booking_id in ids


@pytest.mark.booking
@pytest.mark.updatebooking
class TestUpdateBooking:

    def test_update_booking_full(self, auth_client):
        booking_id, _ = create_booking(auth_client)
        new_payload = valid_booking_payload()
        new_payload["firstname"] = "AlinaNew"
        new_payload["lastname"] = "RozhkoNew"
        new_payload["bookingdates"]["checkin"] = "2025-02-02"
        new_payload["depositpaid"] = False
        new_payload["price"] = "555"

        response = update_booking_full(auth_client, booking_id, new_payload)
        assert response.status_code == 200, "Booking was not updated"

        # GET updated booking
        get_resp = auth_client.get(f"/booking/{booking_id}")
        assert get_resp.status_code == 200

        body = get_resp.json()

        # validate fields
        assert body["firstname"] == "AlinaNew"
        assert body["lastname"] == "RozhkoNew"
        assert body["bookingdates"]["checkin"] == "2025-02-02"
        assert body["depositpaid"] is False

    def test_update_booking_partial(self, auth_client):
        booking_id, _ = create_booking(auth_client)

        patch_payload = {
            "firstname": "OnlyPatched"}

        response = update_booking_partial(auth_client, booking_id, patch_payload)

        assert response.status_code == 200

        get_resp = auth_client.get(f"/booking/{booking_id}")
        body = get_resp.json()

        assert body["firstname"] == "OnlyPatched"

    def test_update_booking_invalid_id(self, client):
        invalid_id = 9999999

        payload = valid_booking_payload()

        response = update_booking_full(client, invalid_id, payload)

        assert response.status_code in (404, 403, 405)


@pytest.mark.booking
@pytest.mark.deletebooking
class TestDeleteBooking:

    def test_delete_booking_success(self, auth_client):
        booking_id, _ = create_booking(auth_client)
        response = delete_booking(auth_client, booking_id)

        assert response.status_code == 201, "Booking was not deleted successfully"
        get_resp = auth_client.get(f"/booking/{booking_id}")
        assert get_resp.status_code in [404, 405], (
            f"Booking still exists after deletion! Status: "
            f"{get_resp.status_code}, body: {get_resp.text}")

    def test_delete_booking_invalid_id(self, auth_client):
        invalid_id = 00000000
        response = delete_booking(auth_client, invalid_id)

        assert response.status_code in [404, 405], (f"Unexpected status code for invalid ID: "
                                                    f"{response.status_code}")

    def test_delete_booking_without_token(self, client):
        booking_id, _ = create_booking(client)
        response = delete_booking(client, booking_id)

        assert response.status_code == 403, (f"Expected 403 for unauthenticated delete, got "
                                             f"{response.status_code}")

    def test_delete_booking_twice(self, auth_client):
        booking_id, _ = create_booking(auth_client)
        response = delete_booking(auth_client, booking_id)
        assert response.status_code == 201

        second_response = delete_booking(auth_client, booking_id)

        assert second_response.status_code in [404, 405], (f"Unexpected status code for invalid ID: "
                                                    f"{response.status_code}")

    def test_delete_booking_then_get_returns_404(self, auth_client):
        booking_id, _ = create_booking(auth_client)
        delete_response = delete_booking(auth_client, booking_id)
        assert delete_response.status_code == 201, "Booking was not deleted"

        get_response = auth_client.get(f"/booking/{booking_id}")
        assert get_response.status_code == 404, (
                    f"Expected 404 after deleting booking, got "
                    f"{get_response.status_code}")

        assert get_response.text.lower() == "not found"


@pytest.mark.booking
@pytest.mark.negativebooking
class TestNegativeBooking:

    def test_create_booking_missing_required_fields(self, client):
        payload = invalid_payload_missing_fields()
        booking_id, response = create_booking(client, payload)

        with pytest.raises(Exception):
            response.json()

        assert response.status_code == 500
        assert booking_id is None
        assert "Internal" in response.text or response.text.strip() != "", (
            f"Unexpected response body: {response.text}")



    def test_create_booking_invalid_dates(self, client):
        payload = invalid_dates_payload()
        booking_id, response = create_booking(client, payload)

        assert response.status_code in (400, 500, 200), (
            f"Unexpected status for invalid dates: {response.status_code}")

        if response.status_code == 200:
            body = response.json().get("booking", {})
            checkin = body.get("bookingdates", {}).get("checkin", "")
            assert checkin != "not-a-date", "Server accepted invalid checkin date"

    def test_update_nonexistent_booking(self, client):
        invalid_id = 999999999
        payload = valid_booking_payload()

        response = update_booking_full(client,booking_id=invalid_id, payload=payload)

        assert response.status_code in (403, 404, 405), (
                    f"Expected 404 or 405 for nonexistent booking update, "
                    f"got {response.status_code}")

    def test_delete_booking_unauthorized(self, client):
        booking_id, _ = create_booking(client)
        response = delete_booking(client, booking_id)

        assert response.status_code == 403, (
                    f"Expected 403 for unauthorized delete, "
                    f"got {response.status_code}")


@pytest.mark.booking
@pytest.mark.negativebooking
class TestBoundaryBooking:

    def test_create_booking_max_length_names(self, client):
        long_name = "A" * 255

        payload = valid_booking_payload()
        payload["firstname"] = long_name
        payload["lastname"] = long_name

        booking_id, response = create_booking(client, payload)

        assert response.status_code == 200, "API failed on max-length strings"
        body = response.json()["booking"]
        assert body["firstname"] == long_name
        assert body["lastname"] == long_name

    def test_create_booking_zero_price(self, client):
        payload = valid_booking_payload()
        payload["totalprice"] = 0

        booking_id, response = create_booking(client, payload)

        assert response.status_code == 200
        assert response.json()["booking"]["totalprice"] == 0

    def test_create_booking_large_price(self, client):
        payload = valid_booking_payload()
        payload["totalprice"] = 10**9

        booking_id, response = create_booking(client, payload)

        assert response.status_code == 200
        assert response.json()["booking"]["totalprice"] == 10**9

    def test_create_booking_far_future_date(self, client):
        payload = valid_booking_payload()
        payload["bookingdates"]["checkin"] = "2100-01-01"
        payload["bookingdates"]["checkout"] = "2100-01-02"

        booking_id, response = create_booking(client, payload)

        assert response.status_code == 200
        assert response.json()["booking"]["bookingdates"]["checkin"] == "2100-01-01"

    def test_create_booking_same_day_checkin_checkout(self, client):
        payload = valid_booking_payload()
        payload["bookingdates"]["checkin"] = "2025-05-05"
        payload["bookingdates"]["checkout"] = "2025-05-05"

        booking_id, response = create_booking(client, payload)

        assert response.status_code in (200, 500), (
            f"Unexpected response for same-day dates: {response.status_code}")

    def test_create_booking_empty_firstname(self, client):
        payload = valid_booking_payload()
        payload["firstname"] = ""

        booking_id, response = create_booking(client, payload)

        # RESTful Booker often still accepts empty strings → 200
        assert response.status_code in (200, 400)

    def test_create_booking_long_additionalneeds(self, client):
        payload = valid_booking_payload()
        payload["additionalneeds"] = "X" * 500

        booking_id, response = create_booking(client, payload)

        assert response.status_code == 200
        assert response.json()["booking"]["additionalneeds"] == "X" * 500

