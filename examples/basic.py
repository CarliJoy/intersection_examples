from typing import Any

from intersection_examples import Intersection


class A:
    test: int

    def foo(self) -> int:
        ...


class B:
    test: int

    def foo(self) -> int:
        ...


test = Intersection[A, B]
print(test)
print(test.test)
print(test.foo)
