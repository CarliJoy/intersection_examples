from typing import overload

from intersection_examples import Intersection


class A:
    @overload
    def foo(self, x: "A") -> "A":
        return 1

    @overload
    def foo(self, x: type) -> type:
        pass

    def foo(self, x: "type | A") -> "type | A":
        pass


class B:
    @overload
    def foo(self, x: int) -> int:
        return 1

    @overload
    def foo(self, x: str) -> str:
        pass

    def foo(self, x: int | str) -> int | str:
        pass


test = Intersection[A, B]
print(test)
print(test.foo)
