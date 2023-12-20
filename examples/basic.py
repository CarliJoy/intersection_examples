from typing import Any

from intersection_examples import Intersection


class A:
    test: int

    def foo(self) -> int:
        return 4


class B:
    test: int

    def foo(self) -> int:
        return 1


test = Intersection[A, B]
print(test)
print(test.test)
print(test.foo)
