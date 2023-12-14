from typing import TypedDict

import pytest

from intersection_examples import Intersection


@pytest.mark.mypy_testing
def test_typed_dict():
    class Movie(TypedDict):
        name: str
        year: int

    class BookBased(TypedDict):
        based_on: str

    class MovieBook(TypedDict):
        name: str
        year: int
        based_on: str

    def foobar1() -> MovieBook:
        return {  # Valid
            "name": "Name",
            "year": 123,
            "based_on": "Movie",
        }

    def foobar2() -> Intersection[Movie, BookBased]:
        return {  # Valid
            "name": "Name",
            "year": 123,
            "based_on": "Movie",
        }
