from typing import TypedDict


class Movie(TypedDict):
    name: str
    year: int


class BookBased(TypedDict):
    based_on: str
