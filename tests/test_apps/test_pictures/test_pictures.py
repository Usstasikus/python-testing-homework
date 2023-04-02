from http import HTTPStatus
from typing import get_args, Union

import pytest
from django.test.client import Client
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse

from server.apps.identity.models import User


FormViewResponse = Union[TemplateResponse, HttpResponseRedirect]

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


def test_create_favourite_picture_with_valid_data(
    user: User,
    user_logged_client: Client,
    favourite_picture_fields: 'FavouritePictureFields'
):
    """Valid data provided must lead to  success creation of a `FavouritePicture`."""
    response: HttpResponse = user_logged_client.post(  # type: ignore[assignment]
        '/pictures/dashboard',
        data=favourite_picture_fields,
    )

    assert isinstance(response, get_args(FormViewResponse))
    assert response.status_code == HTTPStatus.FOUND
    assert response['location'] == '/pictures/dashboard'
    assert user.pictures.filter(**favourite_picture_fields).exists()


def test_dashboard_picture_list(user_logged_client: Client):
    """Dashboard must contain picture list."""
    response = user_logged_client.get('/pictures/dashboard')

    assert response.status_code == HTTPStatus.OK
    assert response.context['pictures']
