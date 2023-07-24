import typing
from basedtyping import Intersection


class A(typing.TypedDict):
    a: int
    common: str


class B(typing.TypedDict):
    b: float
    common: bytes


class Intersected(typing.TypedDict):
    a: int
    b: float
    common: str | bytes


def is_equal(var: Intersection[A, B]) -> Intersected:  # The two representations are equal
    return var  # no type error
