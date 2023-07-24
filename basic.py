from typing import Protocol, overload, reveal_type, runtime_checkable

from basedtyping import Intersection


class A(str):
    a: str


class B(float):
    b: str


AB = Intersection[A, B]


@runtime_checkable
class AB_proto(Protocol):
    a: str
    b: str


class Foo:
    a: str
    b: str
    d: str


assert isinstance(Foo(), AB_proto)
assert isinstance(Foo(), AB)


## Edge Case

Empty = Intersection[int, str]


class One:
    def foo(self, a: int) -> str:
        ...


class Two:
    def foo(self, a: int) -> int:
        ...


AlsoEmpty = Intersection[One, Two]


class OkayOne:
    def foo(self, a: int) -> str:
        ...


class OkayTwo:
    def foo(self, a: str) -> int:
        ...


class IntersectionOneTwo:
    @overload
    def foo(self, a: int) -> str:
        ...

    @overload
    def foo(self, a: str) -> int:
        ...


intersection_one_two = IntersectionOneTwo()
reveal_type(intersection_one_two.foo("a"))
reveal_type(intersection_one_two.foo(object))
