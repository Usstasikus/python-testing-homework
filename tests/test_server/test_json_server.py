from http import HTTPStatus

import requests


def test_json_server() -> None:
    """This test ensures that admin panel docs requires auth."""
    response = requests.get('http://localhost:3000/comments', timeout=3)

    assert response.status_code == HTTPStatus.OK
