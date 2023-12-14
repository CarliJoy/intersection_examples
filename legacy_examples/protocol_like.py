from typing import Protocol, overload, reveal_type

from basedtyping import Intersection


class A1:
    a: str


class A2:
    a: str


class A3:
    a: str


class AProtocol(Protocol):
    a: str


class ACombined(A1, A2):
    ...


def foo(a: Intersection[A1, A2]) -> None:
    ...


def foo_protocol(a: Intersection[A1, AProtocol]):
    ...


foo(A3())

foo_protocol(A3())

foo(ACombined())
foo_protocol(ACombined())


class A:
    foo: str


class AProto(Protocol):
    def foobar(self, i: int) -> str:
        ...


class BProto(Protocol):
    def foobar(self, i: int) -> int:
        ...


new = Intersection[
    AProto, BProto
]  # should give an Type Error, as overload is not working


class ManualOverload(Protocol):
    @overload
    def foobar(self, i: int) -> str:
        ...

    @overload
    def foobar(self, i: int) -> int:
        ...

    def foobar(self, i: int) -> str | int:
        ...


def do(x: Intersection[BProto, AProto]):
    reveal_type(x.foobar)
    reveal_type(x.foobar(10))
    # reveal_type(x.foobar(x="str"))


def that(x: ManualOverload):
    reveal_type(x.foobar)
    reveal_type(x.foobar(10))
