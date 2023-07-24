from typing import TypeVar

from basedtyping import Intersection
from typing_extensions import reveal_type

T = TypeVar("T")


class Enhanced:
    is_great: bool


def enhance(cls: type[T]) -> type[Intersection[T, Enhanced]]:
    class New(cls, Enhanced):
        ...

    return New


reveal_type(enhance(str))  # okay
reveal_type(enhance(None))  # raises a TypeError
