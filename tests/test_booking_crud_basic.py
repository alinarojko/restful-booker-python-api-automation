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

        assert elapsed < 0.5, (
            f"GET /booking/{booking_id} too slow: {elapsed} seconds")

    def test_get_booking_schema_validation(self, client):
        booking_id, _ = create_booking(client)
        response = get_booking(client, booking_id)
        data = response.json()
        schema_path = "./schemas/booking_schema.json"

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

    def test_filters_checkin_date(self, client):
        booking_id, response = create_booking(client)
        checkin_date = response.json()["booking"]["bookingdates"]["checkin"]

        resp = client.get("/booking", params={"checkin": checkin_date})
        assert resp.status_code == 200
        ids = [item["bookingid"] for item in resp.json()]
        assert booking_id in ids

    def test_filter_by_multiple_params(self, client):
        booking_id, response = create_booking(client)
        body = response.json()["booking"]

        firstname = body["firstname"]
        checkin = body["bookingdates"]["checkin"]

        resp = client.get("/booking", params={"firstname": firstname, "checkin": checkin})
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
@pytest.mark.updatebooking
class TestDeleteBooking:
    pass



class TestNegativeBooking:
    pass


class TestBoundaryBooking:
    pass
