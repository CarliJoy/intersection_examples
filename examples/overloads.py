from typing import Any

from intersection_examples import Intersection


class A:
    def foo(self, x: str) -> str:
        pass


class B:
    def foo(self, x: int) -> int:
        return 1


class C:
    def foo(self, x: str) -> int:
        return 1


test = Intersection[A, B]
print(test)
print(test.foo)

try:
    test = Intersection[A, C]
    assert False
except TypeError:
    pass
