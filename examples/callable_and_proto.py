from typing import Callable, Protocol

from intersection_examples import Intersection


class Proto(Protocol):
    def __call__(self, x: int, /) -> str:
        ...


test = Intersection[Callable[[int, str], int], Proto]
print(test.__call__)
print(test.must_subclass)
print()
test = Intersection[Proto, Callable[[int], int]]
print(test.__call__)
print(test.must_subclass)
