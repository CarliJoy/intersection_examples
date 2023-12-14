from typing import Protocol

from intersection_examples import Intersection, get_type_hints


def test_class_intersect():
    class A(str):
        a: str

    class B(float):
        b: str

    AB = Intersection[A, B]

    class AB_proto(Protocol):
        a: str
        b: str

    assert get_type_hints(AB) == get_type_hints(AB_proto)


def test_differing_methods():
    class A:
        def foo(self, a: int) -> str:
            ...

    class B:
        def foo(self, a: int) -> int:
            ...

    class AB_proto(Protocol):
        pass

    AB = Intersection[A, B]

    assert get_type_hints(AB) == get_type_hints(AB_proto)
