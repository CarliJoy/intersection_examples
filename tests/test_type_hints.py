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
