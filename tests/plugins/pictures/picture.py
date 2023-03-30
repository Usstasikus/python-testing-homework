from typing import Protocol, TypedDict, final

import pytest
from django_fakery.faker_factory import Factory
from mimesis.schema import Field, Schema
from typing_extensions import Unpack

from server.apps.pictures.models import FavouritePicture


class FavouritePictureFields(TypedDict, total=False):
    """Fields required for `FavouritePicture`."""
    picture_id: int
    url: str


@final
class FavouritePictureFieldsFactory(Protocol):
    """A factory to generate `FavouritePictureFields`."""

    def __call__(
        self,
        **fields: Unpack[FavouritePictureFields],
    ) -> FavouritePictureFields:
        """`FavouritePictureData` factory protocol."""


@pytest.fixture()
def favourite_picture_fields_factory(mf: Field):
    """Creates a factory to generate a `FavouritePictureFields` dict."""
    def factory(**fields: Unpack[FavouritePictureFields]) -> FavouritePictureFields:
        schema = Schema(
            schema=lambda: {
                'foreign_id': mf('numeric.increment'),
                'url': mf('internet.url'),
            },
        )
        return {
            **next(schema.iterator(1)),
            **fields
        }
    return factory


@pytest.fixture()
def favourite_picture_fields(
    favourite_picture_fields_factory,
) -> FavouritePictureFields:
    """Generates a `FavouritePictureFields`."""
    return favourite_picture_fields_factory()


@final
class FavouritePictureFactory(Protocol):
    """A factory to generate a `FavouritePicture` dict."""

    def __call__(self, **fields) -> FavouritePicture:
        """`FavouritePicture` factory protocol."""


@pytest.fixture()
def favourite_picture_factory(
    fakery: Factory[FavouritePictureFields],
    faker_seed: int,
) -> FavouritePictureFactory:
    """Creates a factory to generate a `FavouritePicture` instance."""
    def factory(**fields):
        return fakery.make(
            model=FavouritePicture,
            fields=fields,
            seed=faker_seed,
        )
    return factory
