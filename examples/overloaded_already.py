from typing import overload

from intersection_examples import IntersectionOp5 as Intersection


class A:
    @overload
    def foo(self, x: "A") -> "A":
        ...

    @overload
    def foo(self, x: type) -> type:
        ...

    def foo(self, x: "type | A") -> "type | A":
        ...


class B:
    @overload
    def foo(self, x: int) -> int:
        ...

    @overload
    def foo(self, x: str) -> str:
        ...

    def foo(self, x: int | str) -> int | str:
        ...


test = Intersection[A, B]
print(test)
print(test.foo)
