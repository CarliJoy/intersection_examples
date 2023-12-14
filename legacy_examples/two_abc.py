from collections.abc import Container, Iterable, Iterator
from typing import TypeVar

from basedtyping import Intersection
from typing_extensions import reveal_type

T = TypeVar("T")


class IterableContainer(Iterable[int], Container[int]):
    ...


def f(x: IterableContainer) -> None:
    ...


def g(x: Intersection[Iterable[int], Container[int]]) -> None:
    if 1 not in x:
        # Debug output
        for it in x:
            print(it)
            reveal_type(it)


class Test(IterableContainer[int]):
    def __iter__(self) -> Iterator[int]:
        yield 1

    def __contains__(self, item: int) -> bool:
        return True


def assertIn(item: T, thing: Intersection[Iterable[T], Container[T]]) -> None:
    if item not in thing:
        # Debug output
        for it in thing:
            print(it)
            reveal_type(it)


f(Test())  # Fails
g(Test())  # Okay
assertIn(1, [1, 2])  # Okay
