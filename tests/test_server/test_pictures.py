from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.test.client import Client

from server.apps.identity.models import User

if TYPE_CHECKING:
    from tests.plugins.pictures.favourite_picture import FavouritePictureFactory


pytestmark = pytest.mark.django_db


def test_favourite_picture_list(
    user: User,
    user_logged_client: Client,
    favourite_picture_factory: 'FavouritePictureFactory',
):
    """Object list contains owned `FavouritePicture` only."""
    selected_pictures = favourite_picture_factory(user=user)
    response = user_logged_client.get('/pictures/favourites')
    assert response.status_code == HTTPStatus.OK
    object_list = list(response.context_data['object_list'])
    assert object_list == [selected_pictures]
