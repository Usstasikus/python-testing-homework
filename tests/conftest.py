"""
This module is used to provide configuration, fixtures, and plugins for pytest.

It may be also used for extending doctest's context:
1. https://docs.python.org/3/library/doctest.html
2. https://docs.pytest.org/en/latest/doctest.html
"""
import pytest
from django.test.client import Client
from mimesis.schema import Field, Schema

from server.apps.identity.models import User


@pytest.fixture()
def user_logged_client(user: User) -> Client:
    """Client logged in as the current user."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture()
def mf(faker_seed: int) -> Field:
    """Returns the current mimesis `Field`."""
    return Field(seed=faker_seed)


pytest_plugins = [
    # Should be the first custom one:
    'plugins.django_settings',
    'plugins.identity.user',
    'plugins.pictures.picture'
    # TODO: add your own plugins here!
]

