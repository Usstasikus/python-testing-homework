import json
from contextlib import contextmanager
from http import HTTPStatus
from typing import Callable, Iterator
from urllib.parse import urljoin

import httpretty
import pytest
import requests
from django.test import Client

from server.apps.pictures.container import container
from server.common.django.types import Settings


@pytest.fixture()
def settings() -> Settings:
    """Get Django settings."""
    return container.resolve(Settings)


@pytest.fixture()
def json_photos():
    """Get photos from json_server."""
    return requests.get(
        'http://localhost:3000/photos',
        timeout=1,
    ).json()


@pytest.fixture()
def mock_pictures_url(
    settings: Settings,
    json_photos,
) -> Callable[[], None]:
    """Route placeholder API endpoint to json-server."""
    @contextmanager
    def factory() -> Iterator[None]:
        with httpretty.httprettized():
            httpretty.register_uri(
                httpretty.GET,
                urljoin(settings.PLACEHOLDER_API_URL, 'photos'),
                body=json.dumps(json_photos),
                content_type='application/json',
            )
            yield
            assert httpretty.has_request()

    return factory


@pytest.mark.django_db()
def test_pictures_same_len(
    user_logged_client: Client,
    mock_pictures_url,
    json_photos,
) -> None:
    """Check dashboard content."""
    with mock_pictures_url():
        response = user_logged_client.get('/pictures/dashboard')
        assert response.status_code == HTTPStatus.OK
        assert len(response.context['pictures']) == len(json_photos)
        assert response.context['pictures'] == json_photos
