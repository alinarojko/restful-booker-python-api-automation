import datetime


def valid_booking_payload():
    # Standard valid payload for creating booking.
    return {
        "firstname": "Alina",
        "lastname": "Rozhko",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2025-01-01",
            "checkout": "2025-01-05"
        },
        "additionalneeds": "Breakfast"
    }


def minimal_payload():
    # Minimal required payload.
    return {
        "firstname": "Test",
        "lastname": "User",
        "totalprice": 1,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2025-02-01",
            "checkout": "2025-02-02"
        }
    }


def invalid_payload_missing_fields():
    # Payload intentionally missing required fields.
    # Used for negative tests_api.
    return {
        "firstname": "Alina"
        # missing lastname, price, depositpaid, bookingdates...
    }


def invalid_dates_payload():
    # Payload with incorrect date format.
    return {
        "firstname": "Alina",
        "lastname": "QA",
        "totalprice": 123,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "not-a-date",
            "checkout": "2025/15/90"
        }
    }
