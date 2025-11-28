import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import pytest

from helpers.booking_helpers import (
    create_booking,
    get_booking,
    update_booking_full,
    update_booking_partial,
    delete_booking)

from helpers.booking_payloads import (
    valid_booking_payload,
    minimal_payload,
    invalid_payload_missing_fields,
    invalid_dates_payload)

import os
import allure


@pytest.mark.createbooking
@pytest.mark.booking
@allure.feature("Booking CRUD")
@allure.story("Create Booking")
class TestCreateBooking:

    @allure.title("Create booking with valid standard payload")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_booking_success(self, client):

        with allure.step("Send POST /booking with valid payload"):
            booking_id, response = create_booking(client)

        with allure.step("Validate response status code"):
            assert response.status_code == 200

        with allure.step("Attach full JSON response"):
            allure.attach(json.dumps(response.json(), indent=2),
                          "response_body",
                          allure.attachment_type.JSON)

        with allure.step("Validate booking exists"):
            assert booking_id is not None
            assert "booking" in response.json()

    @allure.title("Create booking using minimal payload")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_booking_minimal_payload(self, client):

        body = minimal_payload()

        with allure.step("POST /booking with minimal payload"):
            booking_id, response = create_booking(client, payload=body)

        allure.attach(json.dumps(body, indent=2),
                      "minimal_payload",
                      allure.attachment_type.JSON)

        allure.attach(json.dumps(response.json(), indent=2),
                      "response_minimal",
                      allure.attachment_type.JSON)

        assert response.status_code == 200
        assert booking_id is not None

        booking = response.json()["booking"]
        assert booking["firstname"] == body["firstname"]
        assert booking["lastname"] == body["lastname"]

    @allure.title("Create booking with unicode & special characters")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_booking_with_special_characters(self, client):

        body = valid_booking_payload()
        body["firstname"] = "Alina-测试-ÄÖÜ"
        body["lastname"] = "O'Connor-测试"

        with allure.step("POST /booking with special characters"):
            booking_id, response = create_booking(client, payload=body)

        allure.attach(json.dumps(body, indent=2),
                      "payload_with_special_chars",
                      allure.attachment_type.JSON)

        allure.attach(json.dumps(response.json(), indent=2),
                      "response_with_special_chars",
                      allure.attachment_type.JSON)

        assert response.status_code == 200
        assert booking_id is not None

        data = response.json()["booking"]
        assert data["firstname"] == body["firstname"]
        assert data["lastname"] == body["lastname"]


@pytest.mark.booking
@pytest.mark.getbooking
@allure.feature("Booking CRUD")
@allure.story("Get Booking By ID")
class TestGetBookingByID:

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("GET Booking by valid ID returns 200 and correct structure")
    def test_get_booking_by_id(self, client):
        with allure.step("Create booking to have a valid ID"):
            booking_id, create_resp = create_booking(client)
            allure.attach(
                json.dumps(create_resp.json(), indent=2),
                name="Created Booking",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step(f"GET booking {booking_id}"):
            response = get_booking(client, booking_id)
            allure.attach(
                response.text,
                name="GET Response",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Validate response"):
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert data.get("firstname")
            assert data.get("lastname")

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("GET Booking for non-existing ID returns 404")
    def test_get_booking_not_found(self, client):
        non_existent_id = 9999999

        with allure.step(f"GET booking {non_existent_id} (should be 404)"):
            response = get_booking(client, non_existent_id)
            allure.attach(
                response.text,
                name="Response 404",
                attachment_type=allure.attachment_type.TEXT
            )

        assert response.status_code == 404

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("GET Booking with invalid ID format returns 400 or 404")
    def test_get_booking_invalid_id_format(self, client):
        invalid_id = "abc"

        with allure.step(f"GET booking with invalid id '{invalid_id}'"):
            response = get_booking(client, invalid_id)
            allure.attach(
                response.text,
                name="Invalid ID Response",
                attachment_type=allure.attachment_type.TEXT
            )

        assert response.status_code in (400, 404)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("GET Booking response time is under 1 second")
    def test_get_booking_performance(self, client):
        booking_id, _ = create_booking(client)

        with allure.step("Measure response time for GET booking"):
            response = get_booking(client, booking_id)
            elapsed = response.elapsed.total_seconds()

            allure.attach(
                str(elapsed),
                name="Response Time (seconds)",
                attachment_type=allure.attachment_type.TEXT
            )

        assert elapsed < 1, f"Too slow: {elapsed}s"

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("GET Booking JSON Schema Validation")
    def test_get_booking_schema_validation(self, client):
        booking_id, _ = create_booking(client)

        with allure.step(f"GET booking {booking_id} for schema validation"):
            response = get_booking(client, booking_id)
            data = response.json()
            allure.attach(
                json.dumps(data, indent=2),
                name="GET Response for Schema",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Load JSON schema"):
            schema_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "schemas", "booking_schema.json")
            )
            with open(schema_path) as f:
                schema = json.load(f)

        with allure.step("Validate schema"):
            try:
                validate(instance=data, schema=schema)
            except ValidationError as e:
                allure.attach(str(e), name="Schema Validation Error", attachment_type=allure.attachment_type.TEXT)
                assert False, f"Schema validation failed: {e.message}"


@pytest.mark.booking
@pytest.mark.getbooking
@allure.feature("Booking CRUD")
@allure.story("Booking Filters")
class TestGetBookingFilters:

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Filter bookings by firstname — correct booking returned")
    def test_get_booking_by_first_name(self, client):
        with allure.step("Create booking and extract firstname"):
            booking_id, response = create_booking(client)
            firstname = response.json()["booking"]["firstname"]
            allure.attach(
                json.dumps(response.json(), indent=2),
                name="Created Booking",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step(f"GET /booking?firstname={firstname}"):
            response = client.get("/booking", params={"firstname": firstname})
            allure.attach(
                response.text,
                name="Filter Response",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Validate booking is returned in filtered results"):
            returned_ids = [item["bookingid"] for item in response.json()]
            assert booking_id in returned_ids, \
                f"Booking ID {booking_id} not in {returned_ids}"

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Filter booking by fullname (firstname + lastname)")
    def test_get_booking_fullname(self, client):
        with allure.step("Create booking and extract full name"):
            booking_id, response = create_booking(client)
            firstname = response.json()["booking"]["firstname"]
            lastname = response.json()["booking"]["lastname"]

            allure.attach(
                json.dumps(response.json(), indent=2),
                name="Created Booking",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step(f"GET /booking?firstname={firstname}&lastname={lastname}"):
            response = client.get(
                "/booking",
                params={"firstname": firstname, "lastname": lastname}
            )
            allure.attach(
                response.text,
                name="Filter Response",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Validate booking is returned"):
            ids = [item["bookingid"] for item in response.json()]
            assert booking_id in ids, \
                f"Booking {booking_id} not found in {ids}"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Filtering with non-existing firstname returns empty list")
    def test_filters_no_result(self, client):
        non_existing = "____NotValidName_____"

        with allure.step(f"GET /booking?firstname={non_existing}"):
            response = client.get("/booking", params={"firstname": non_existing})
            allure.attach(
                response.text,
                name="Empty Filter Response",
                attachment_type=allure.attachment_type.JSON
            )

        assert response.status_code == 200
        assert response.json() == [], "Expected empty list"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Filter by multiple params (firstname + lastname)")
    def test_filter_by_multiple_params(self, client):
        with allure.step("Create booking and extract firstname, lastname"):
            booking_id, response = create_booking(client)
            body = response.json()["booking"]
            firstname = body["firstname"]
            lastname = body["lastname"]

            allure.attach(
                json.dumps(response.json(), indent=2),
                name="Created Booking",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step(
            f"GET /booking?firstname={firstname}&lastname={lastname}"
        ):
            resp = client.get(
                "/booking",
                params={"firstname": firstname, "lastname": lastname}
            )
            allure.attach(
                resp.text,
                name="Filtered Response",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Validate booking ID is included in results"):
            ids = [item["bookingid"] for item in resp.json()]
            assert booking_id in ids, \
                f"Booking ID {booking_id} not found in {ids}"


@pytest.mark.booking
@pytest.mark.updatebooking
@allure.feature("Booking CRUD")
@allure.story("Update Booking")
class TestUpdateBooking:

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Full update of an existing booking")
    def test_update_booking_full(self, auth_client):
        with allure.step("Create booking for update"):
            booking_id, response = create_booking(auth_client)
            created = response.json()["booking"]

            allure.attach(
                json.dumps(created, indent=2),
                name="Created Booking",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Prepare full update payload"):
            new_payload = valid_booking_payload()
            new_payload["firstname"] = "AlinaNew"
            new_payload["lastname"] = "RozhkoNew"
            new_payload["bookingdates"]["checkin"] = "2025-02-02"
            new_payload["depositpaid"] = False
            new_payload["totalprice"] = 555

            allure.attach(
                json.dumps(new_payload, indent=2),
                name="Update Payload",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step(f"PUT /booking/{booking_id} — full update"):
            response = update_booking_full(auth_client, booking_id, new_payload)
            allure.attach(
                response.text,
                name="PUT Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert response.status_code == 200, "Booking was not updated"

        with allure.step("GET updated booking and validate fields"):
            updated = auth_client.get(f"/booking/{booking_id}")
            allure.attach(
                updated.text,
                name="Updated Booking Response",
                attachment_type=allure.attachment_type.JSON
            )

            body = updated.json()

            assert body["firstname"] == "AlinaNew"
            assert body["lastname"] == "RozhkoNew"
            assert body["bookingdates"]["checkin"] == "2025-02-02"
            assert body["depositpaid"] is False

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Partial update of an existing booking")
    def test_update_booking_partial(self, auth_client):
        with allure.step("Create booking to patch"):
            booking_id, response = create_booking(auth_client)
            created = response.json()["booking"]

            allure.attach(
                json.dumps(created, indent=2),
                name="Created Booking",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Prepare partial update payload"):
            patch_payload = {"firstname": "OnlyPatched"}
            allure.attach(
                json.dumps(patch_payload, indent=2),
                name="PATCH Payload",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step(f"PATCH /booking/{booking_id} — partial update"):
            response = update_booking_partial(auth_client, booking_id, patch_payload)
            allure.attach(
                response.text,
                name="PATCH Response",
                attachment_type=allure.attachment_type.JSON
            )
            assert response.status_code == 200

        with allure.step("Verify patched firstname"):
            updated = auth_client.get(f"/booking/{booking_id}")
            body = updated.json()
            allure.attach(
                json.dumps(body, indent=2),
                name="After PATCH",
                attachment_type=allure.attachment_type.JSON
            )
            assert body["firstname"] == "OnlyPatched"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Attempt to update booking using invalid ID")
    def test_update_booking_invalid_id(self, client):
        invalid_id = 9999999

        with allure.step("Prepare valid update payload for invalid ID"):
            payload = valid_booking_payload()
            allure.attach(
                json.dumps(payload, indent=2),
                name="Payload Sent to Invalid ID",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step(f"PUT /booking/{invalid_id} — expecting error"):
            response = update_booking_full(client, invalid_id, payload)

            allure.attach(
                response.text,
                name="Invalid Update Response",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code in (404, 403, 405), \
                f"Unexpected status code: {response.status_code}"


@pytest.mark.booking
@pytest.mark.deletebooking
@allure.feature("Booking CRUD")
@allure.story("Delete Booking")
class TestDeleteBooking:

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Successful deletion of an existing booking")
    def test_delete_booking_success(self, auth_client):
        with allure.step("Create booking for deletion"):
            booking_id, response = create_booking(auth_client)
            booking_data = response.json()["booking"]

            allure.attach(
                json.dumps(booking_data, indent=2),
                name="Created Booking",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step(f"DELETE /booking/{booking_id}"):
            response = delete_booking(auth_client, booking_id)
            allure.attach(
                response.text,
                name="Delete Response",
                attachment_type=allure.attachment_type.TEXT
            )
            assert response.status_code == 201, "Booking was not deleted successfully"

        with allure.step("Verify booking no longer exists"):
            get_resp = auth_client.get(f"/booking/{booking_id}")

            allure.attach(
                get_resp.text,
                name="GET After Deletion",
                attachment_type=allure.attachment_type.TEXT
            )

            assert get_resp.status_code in [404, 405], \
                f"Booking still exists! GET returned {get_resp.status_code}"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Deletion attempt for invalid booking ID")
    def test_delete_booking_invalid_id(self, auth_client):
        invalid_id = 0

        with allure.step("Attempt delete for invalid ID"):
            response = delete_booking(auth_client, invalid_id)

            allure.attach(
                response.text,
                name="Delete Invalid ID Response",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code in [404, 405], \
                f"Unexpected status code for invalid ID: {response.status_code}"

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Attempt to delete booking without authentication token")
    def test_delete_booking_without_token(self, client):
        with allure.step("Create booking (no auth required)"):
            booking_id, _ = create_booking(client)

        with allure.step("Attempt DELETE without token"):
            response = delete_booking(client, booking_id)

            allure.attach(
                response.text,
                name="Unauthorized Delete Response",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 403, \
                f"Expected 403 for unauthenticated delete, got {response.status_code}"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Delete booking twice → second delete should return 404/405")
    def test_delete_booking_twice(self, auth_client):
        with allure.step("Create booking for double delete"):
            booking_id, _ = create_booking(auth_client)

        with allure.step("First DELETE request"):
            first_resp = delete_booking(auth_client, booking_id)

            allure.attach(
                first_resp.text,
                name="First Delete Response",
                attachment_type=allure.attachment_type.TEXT
            )

            assert first_resp.status_code == 201

        with allure.step("Second DELETE request → expect 404/405"):
            second_resp = delete_booking(auth_client, booking_id)

            allure.attach(
                second_resp.text,
                name="Second Delete Response",
                attachment_type=allure.attachment_type.TEXT
            )

            assert second_resp.status_code in [404, 405], \
                f"Expected 404 or 405 for second delete, got {second_resp.status_code}"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("GET after deletion should return 404 Not Found")
    def test_delete_booking_then_get_returns_404(self, auth_client):
        with allure.step("Create booking"):
            booking_id, _ = create_booking(auth_client)

        with allure.step("DELETE booking"):
            delete_resp = delete_booking(auth_client, booking_id)
            allure.attach(
                delete_resp.text,
                name="Delete Response",
                attachment_type=allure.attachment_type.TEXT
            )
            assert delete_resp.status_code == 201, "Booking was not deleted"

        with allure.step("GET deleted booking → expect 404"):
            get_resp = auth_client.get(f"/booking/{booking_id}")

            allure.attach(
                get_resp.text,
                name="GET After Deletion",
                attachment_type=allure.attachment_type.TEXT
            )

            assert get_resp.status_code == 404, \
                f"Expected 404 after deletion, got {get_resp.status_code}"

            assert get_resp.text.lower() == "not found"


@pytest.mark.booking
@pytest.mark.negativebooking
@allure.feature("Booking CRUD")
@allure.story("Negative Scenarios")
class TestNegativeBooking:

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Create booking with missing required fields → expect failure")
    def test_create_booking_missing_required_fields(self, client):
        payload = invalid_payload_missing_fields()

        with allure.step("Send POST /booking with missing fields"):
            booking_id, response = create_booking(client, payload)

            allure.attach(
                json.dumps(payload, indent=2),
                name="Invalid Payload (Missing Fields)",
                attachment_type=allure.attachment_type.JSON
            )

            allure.attach(
                response.text,
                name="Response Body",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Validate failure response"):
            assert response.status_code == 500
            assert booking_id is None
            assert "Internal" in response.text or response.text.strip() != ""

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with invalid dates (e.g., 'not-a-date')")
    def test_create_booking_invalid_dates(self, client):
        payload = invalid_dates_payload()

        with allure.step("Send POST /booking with invalid dates"):
            booking_id, response = create_booking(client, payload)

            allure.attach(
                json.dumps(payload, indent=2),
                name="Invalid Dates Payload",
                attachment_type=allure.attachment_type.JSON
            )

            allure.attach(
                response.text,
                name="Response Body",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Validate response"):
            assert response.status_code in (400, 500, 200)

            if response.status_code == 200:
                body = response.json().get("booking", {})
                assert body.get("bookingdates", {}).get("checkin") != "not-a-date", \
                    "Server incorrectly accepted invalid date"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Update nonexistent booking → expect 404 or 405")
    def test_update_nonexistent_booking(self, client):
        invalid_id = 999999999
        payload = valid_booking_payload()

        with allure.step(f"Send PUT /booking/{invalid_id} for nonexistent booking"):
            response = update_booking_full(client, booking_id=invalid_id, payload=payload)

            allure.attach(
                json.dumps(payload, indent=2),
                name="Payload for Nonexistent Booking",
                attachment_type=allure.attachment_type.JSON
            )

            allure.attach(
                response.text,
                name="Response Body",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Validate error response"):
            assert response.status_code in (403, 404, 405), \
                f"Unexpected status: {response.status_code}"

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Delete booking without authentication → expect 403 (forbidden)")
    def test_delete_booking_unauthorized(self, client):
        with allure.step("Create booking with no auth"):
            booking_id, _ = create_booking(client)

        with allure.step("Attempt to DELETE without token"):
            response = delete_booking(client, booking_id)

            allure.attach(
                response.text,
                name="Unauthorized Delete Response",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Validate 403"):
            assert response.status_code == 403, \
                f"Expected 403, got {response.status_code}"


@pytest.mark.booking
@pytest.mark.negativebooking
@allure.feature("Booking CRUD")
@allure.story("Boundary Value Testing")
class TestBoundaryBooking:

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with maximum length names (255 chars)")
    def test_create_booking_max_length_names(self, client):
        long_name = "A" * 255
        payload = valid_booking_payload()
        payload["firstname"] = long_name
        payload["lastname"] = long_name

        with allure.step("Send POST /booking with 255-char names"):
            booking_id, response = create_booking(client, payload)

            allure.attach(
                json.dumps(payload, indent=2),
                name="Payload (255-char names)",
                attachment_type=allure.attachment_type.JSON
            )
            allure.attach(response.text, "Response Body",
                          allure.attachment_type.TEXT)

        with allure.step("Validate creation with 255-char names"):
            assert response.status_code == 200
            body = response.json()["booking"]
            assert body["firstname"] == long_name
            assert body["lastname"] == long_name

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with zero price")
    def test_create_booking_zero_price(self, client):
        payload = valid_booking_payload()
        payload["totalprice"] = 0

        with allure.step("Send POST /booking with totalprice = 0"):
            booking_id, response = create_booking(client, payload)

            allure.attach(
                json.dumps(payload, indent=2),
                name="Payload (totalprice=0)",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Validate zero price accepted"):
            assert response.status_code == 200
            assert response.json()["booking"]["totalprice"] == 0

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with extremely large price (1B)")
    def test_create_booking_large_price(self, client):
        payload = valid_booking_payload()
        payload["totalprice"] = 10**9

        with allure.step("Send POST /booking with huge totalprice"):
            booking_id, response = create_booking(client, payload)

            allure.attach(
                json.dumps(payload, indent=2),
                name="Payload (1B price)",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Validate extremely large price accepted"):
            assert response.status_code == 200
            assert response.json()["booking"]["totalprice"] == 10**9

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with far-future dates (year 2100)")
    def test_create_booking_far_future_date(self, client):
        payload = valid_booking_payload()
        payload["bookingdates"]["checkin"] = "2100-01-01"
        payload["bookingdates"]["checkout"] = "2100-01-02"

        with allure.step("Send POST /booking with year 2100 dates"):
            booking_id, response = create_booking(client, payload)

            allure.attach(
                json.dumps(payload, indent=2),
                name="Payload (far-future dates)",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Validate far-dates accepted"):
            assert response.status_code == 200
            assert response.json()["booking"]["bookingdates"]["checkin"] == "2100-01-01"

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Create booking with same-day checkin and checkout")
    def test_create_booking_same_day_checkin_checkout(self, client):
        payload = valid_booking_payload()
        payload["bookingdates"]["checkin"] = "2025-05-05"
        payload["bookingdates"]["checkout"] = "2025-05-05"

        with allure.step("Send POST /booking with same-day dates"):
            booking_id, response = create_booking(client, payload)
            allure.attach(json.dumps(payload, indent=2),
                          "Payload (same-day dates)",
                          allure.attachment_type.JSON)

        with allure.step("Validate API behaviour (200 or 500 allowed)"):
            assert response.status_code in (200, 500)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with empty firstname")
    def test_create_booking_empty_firstname(self, client):
        payload = valid_booking_payload()
        payload["firstname"] = ""

        with allure.step("Send POST /booking with empty firstname"):
            booking_id, response = create_booking(client, payload)

            allure.attach(
                json.dumps(payload, indent=2),
                name="Payload (empty firstname)",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Validate API behaviour (200 or 400 allowed)"):
            assert response.status_code in (200, 400)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Create booking with very long additionalneeds (500 chars)")
    def test_create_booking_long_additionalneeds(self, client):
        payload = valid_booking_payload()
        payload["additionalneeds"] = "X" * 500

        with allure.step("Send POST /booking with 500-char field"):
            booking_id, response = create_booking(client, payload)

            allure.attach(
                json.dumps(payload, indent=2),
                name="Payload (500-char additionalneeds)",
                attachment_type=allure.attachment_type.JSON
            )

        with allure.step("Validate long text accepted"):
            assert response.status_code == 200
            assert response.json()["booking"]["additionalneeds"] == "X" * 500
