from helpers.booking_payloads import valid_booking_payload
from helpers.api_client import APIClient


def create_booking(client, payload=None):
    # Creates a booking using the provided client.
    # Returns (booking_id, full_response).

    body = payload or valid_booking_payload()
    response = client.post("/booking", json=body)

    booking_id = None
    try:
        data = response.json()
        booking_id = data.get("bookingid")
    except Exception:
        booking_id = None

    return booking_id, response


def get_booking(client, booking_id: int):
    # Retrieves booking details by ID.
    return client.get(f"/booking/{booking_id}")


def delete_booking(client, booking_id: int):
    # Deletes a booking. Requires an authenticated client.
    return client.delete(f"/booking/{booking_id}")


def update_booking_full(client, booking_id: int, payload: dict):
    # Performs full update (PUT) of booking.
    return client.put(f"/booking/{booking_id}", json=payload)


def update_booking_partial(client, booking_id: int, payload: dict):
    # Performs partial update (PATCH).
    return client.patch(f"/booking/{booking_id}", json=payload)
