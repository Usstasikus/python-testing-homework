from http import HTTPStatus
from typing import TYPE_CHECKING, get_args, Union

from django.test import Client
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
import pytest

from server.apps.identity.models import User

FormViewResponse = Union[TemplateResponse, HttpResponseRedirect]

pytestmark = pytest.mark.django_db


# if TYPE_CHECKING:
#     from tests.plugins.identity.user import UserAssertion, UserData


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
    """This test ensures user registration with valid data is success."""
    response = client.post('/identity/registration', data=registration_data)

    assert response.status_code == HTTPStatus.FOUND, (
        response.context['form'].errors
    )

    user = User.objects.get(email=registration_data['email'])

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
    """This test ensures user registration with missing data is not success."""
    response = client.post(
        '/identity/registration',
        data=registration_data | {missing_field: ''},
    )

    assert response.status_code == HTTPStatus.OK
    assert missing_field in response.context['form'].errors
    assert not User.objects.filter(email=registration_data['email'])


def test_invalid_password_registration(
    client: Client,
    user_password: str,
    user_second_password: str,
    registration_data,
    assert_correct_user: 'UserAssertion',
) -> None:
    """This test ensures user registration with inconsistent password data is not success."""
    response = client.post(
        '/identity/registration',
        data=registration_data | {"password2": user_second_password}
    )

    assert response.status_code == HTTPStatus.OK
    assert 'password2' in response.context['form'].errors
    assert not User.objects.filter(email=registration_data['email']).exists()


def test_valid_credentials_login(
    client: Client,
    user: User,
    user_password: str
):
    """User login with valid credentials must be success."""
    request_data = {'username': user.email, 'password': user_password}

    response: HttpResponse = client.post(
        '/identity/login',
        data=request_data,
    )

    assert isinstance(response, get_args(FormViewResponse))
    assert response.status_code == HTTPStatus.FOUND
    assert response['location'] == '/pictures/dashboard'


@pytest.mark.parametrize(
    'invalid_field',
    [['username'], ['password']],
)
def test_invalid_credentials_login(
    client: Client,
    user: User,
    user_password: str,
    invalid_field: str,
):
    """User login with invalid credentials must fail."""
    request_data = {'username': user.email, 'password': user_password}
    for curr_invalid_field in invalid_field:
        request_data[curr_invalid_field] = (
            'invalid'.format(request_data[curr_invalid_field])
        )

    response: HttpResponse = client.post(
        '/identity/login',
        data=request_data,
    )

    assert isinstance(response, get_args(FormViewResponse))
    assert response.status_code == HTTPStatus.OK
    assert response.context_data
    assert curr_invalid_field in response.context_data['form'].errors \
           or "__all__" in response.context_data['form'].errors


def test_inactive_user_login(
    client: Client,
    user_inactive: User,
    user_password: str
):
    """User login with credentials of an inactive must fail."""
    request_data = {'username': user_inactive.email, 'password': user_password}

    response: HttpResponse = client.post(
        '/identity/login',
        data=request_data,
    )

    assert isinstance(response, get_args(FormViewResponse))
    assert response.status_code == HTTPStatus.OK
    assert response.context_data
    assert '__all__' in response.context_data['form'].errors

