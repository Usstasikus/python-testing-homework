import datetime
from typing import final, Callable, Protocol, TypedDict
from typing_extensions import Unpack

from django_fakery.faker_factory import Factory

from mimesis.schema import Field, Schema
import pytest

from server.apps.identity.models import User

USER_BIRTHDAY_FORMAT = '%Y-%m-%d'


@final
class UserData(TypedDict, total=False):
    """
    Represent the simplified user data that is required to create a new user.
    It does not include ``password``, because it is very special in django.
    Importing this type is only allowed under ``if TYPE_CHECKING`` in tests.
    """
    email: str
    last_name: str
    first_name: str
    date_of_birth: str
    address: str
    job_title: str
    phone: str


@final
class RegistrationData(UserData, total=False):
    """
    Represent the registration data that is required to create a new user.
    Importing this type is only allowed under ``if TYPE_CHECKING`` in tests.
    """
    password1: str
    password2: str


@final
class UserDataFactory(Protocol):
    def __call__(self, **fields: Unpack[UserData]) -> UserData:
        """User data factory protocol."""


@final
class RegistrationDataFactory(Protocol):
    def __call__(self, **fields: Unpack[RegistrationData]) -> RegistrationData:
        """Registration data factory protocol."""


@pytest.fixture
def user_data_factory(mf) -> RegistrationDataFactory:
    """A factory to generate a `RegistrationData` dict."""
    def factory(**fields: Unpack[RegistrationData]) -> RegistrationData:
        schema = Schema(
            schema=lambda: {
                'email': mf('person.email'),
                'first_name': mf('person.first_name'),
                'last_name': mf('person.last_name'),
                'date_of_birth': mf(
                    'datetime.formatted_date',
                    fmt=USER_BIRTHDAY_FORMAT,
                    end=datetime.date.today().year - 1,
                ),
                'address': mf('address.address'),
                'job_title': mf('person.occupation'),
                'phone': mf('person.telephone'),

            }
        )
        return {
            **schema.create(iterations=1)[0],
            **fields
        }

    return factory


@pytest.fixture
def user_data(user_data_factory: UserDataFactory) -> UserData:
    return user_data_factory()


UserAssertion = Callable[[User, UserData], None]

@pytest.fixture(scope='session')
def assert_correct_user() -> UserAssertion:
    def factory(user: User, expected: UserData) -> None:
        assert user.id
        assert user.is_active
        assert not user.is_superuser
        assert not user.is_staff
        # All other fields:
        assert user.first_name == expected['first_name']
        assert user.last_name == expected['last_name']
        if user.date_of_birth:
            assert (
                user.date_of_birth.strftime(USER_BIRTHDAY_FORMAT)
                == expected['date_of_birth']
            )
        else:
            assert not expected['date_of_birth']
        assert user.address == expected['address']
        assert user.job_title == expected['job_title']
        assert user.phone == expected['phone']

    return factory


@pytest.fixture
def new_user_password(mf) -> str:
    """Password of the current user."""
    return mf('person.password')


@pytest.fixture
def user_password(new_user_password: str) -> str:
    return new_user_password


@pytest.fixture
def user_second_password(mf) -> str:
    return mf('person.password')


@pytest.fixture
def user_email(mf) -> str:
    return mf('person.email')


@final
class UserFactory(Protocol):  # type: ignore[misc]
    """A factory to generate a `User` instance."""

    def __call__(self, **fields) -> User:
        """Profile data factory protocol."""


@pytest.fixture()
def user_factory(fakery: Factory[User], faker_seed: int) -> UserFactory:
    """Creates a factory to generate a user instance."""
    return fakery.m(User, seed=faker_seed)


@pytest.fixture()
def user(
    user_factory: UserFactory,
    user_email: str,
    user_password: str,
) -> User:
    """The current user fixture.
    """
    return user_factory(
        email=user_email,
        password=user_password,
        is_active=True,
    )


@pytest.fixture()
def user_inactive(
    user_factory: UserFactory,
    user_email: str,
    user_password: str,
) -> User:
    """The current inactive user fixture.
    """
    return user_factory(
        email=user_email,
        password=user_password,
        is_active=False,
    )
