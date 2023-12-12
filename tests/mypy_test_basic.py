from typing import Protocol, get_type_hints, overload, reveal_type, runtime_checkable

import pytest
from basedtyping import Intersection


@pytest.mark.mypy_testing
def test_class_intersect():
    class A(str):
        a: str

    class B(float):
        b: str

    AB = Intersection[A, B]

    @runtime_checkable
    class AB_proto(Protocol):
        a: str
        b: str

    # print(get_type_hints(AB_proto))
    # print(get_type_hints(AB))

    print(reveal_type(AB))  # R: object
    print(reveal_type(AB_proto))  # R: def () -> mypy_test_basic.AB_proto@19
