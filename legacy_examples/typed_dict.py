from typing import TypedDict

from basedtyping import Intersection


class Movie(TypedDict):
    name: str
    year: int


class BookBased(TypedDict):
    based_on: str


class MovieBook(TypedDict):
    name: str
    year: int
    based_on: str


def foobar() -> Intersection[Movie, BookBased]:
    return {
        "name": "Name",
        "year": 123,
        "based_on": "Movie",
    }
