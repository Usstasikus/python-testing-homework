from http import HTTPStatus
from typing import TYPE_CHECKING

from django.test import Client
import pytest

from server.apps.identity.models import User


pytestmark = pytest.mark.django_db


if TYPE_CHECKING:
    from tests.plugins.identity.user import UserAssertion, UserData


@pytest.fixture
def registration_data(
    user_password: str,
    user_data: 'UserData',
):
    return {
        **user_data,
        'password1': user_password,
        'password2': user_password,
    }

def test_valid_registration(
    client: Client,
    user_password: str,
    registration_data,
    assert_correct_user: 'UserAssertion',
) -> None:
    response = client.post('/identity/registration', data=registration_data)
    assert response.status_code == HTTPStatus.FOUND, (
        response.context['form'].errors
    )
    user = User.objects.all().get(email=registration_data['email'])
    assert user.check_password(user_password)
    assert_correct_user(user, registration_data)


@pytest.mark.parametrize(
    'missing_field',
    User.REQUIRED_FIELDS + [User.USERNAME_FIELD],
)
def test_registration_missing_required_field(
    client: Client,
    registration_data,
    missing_field: str,
) -> None:
    response = client.post(
        '/identity/registration',
        data=registration_data | {missing_field: ''},
    )
    assert response.status_code == HTTPStatus.OK
    assert missing_field in response.context['form'].errors
    assert not User.objects.filter(email=registration_data['email']).exists()


def test_invalid_password_registration(
    client: Client,
    user_password: str,
    user_second_password: str,
    registration_data,
    assert_correct_user: 'UserAssertion',
) -> None:
    response = client.post(
        '/identity/registration',
        data=registration_data | {"password2": user_second_password}
    )

    assert response.status_code == HTTPStatus.OK
    assert 'password2' in response.context['form'].errors
    assert not User.objects.filter(email=registration_data['email']).exists()
