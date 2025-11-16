import requests


def test_healthcheck():
    url = "https://restful-booker.herokuapp.com/ping"
    response = requests.get(url)
    assert response.status_code == 201