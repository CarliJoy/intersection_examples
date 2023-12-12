from typing import Any, Protocol, cast, reveal_type

import pytest

from intersection_examples import Intersection


@pytest.mark.mypy_testing
def test_class_intersect():
    class A(str):
        a: str

    class B(float):
        b: str

    AB = Intersection[A, B]

    class AB_proto(Protocol):
        a: str
        b: str

    print(reveal_type(AB))  # R: object
    print(reveal_type(AB_proto))  # R: def () -> mypy_test_basic.AB_proto@16
