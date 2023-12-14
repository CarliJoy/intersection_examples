import typing

import pytest

from intersection_examples import Intersection


@pytest.mark.mypy_testing
def test_typed_dicts():
    class A(typing.TypedDict):
        a: int
        common: str

    class B(typing.TypedDict):
        b: float
        common: bytes

    class C(A, B):
        pass

    class Intersected(typing.TypedDict):
        a: int
        b: float
        common: str | bytes

    def is_equal(
        var: Intersection[A, B]
    ) -> Intersected:  # The two representations are equal # NOTE: Changed from original
        # as needs to assert that it exposes the same interface, rather than something
        # that is a subclass of A and B
        return Intersected(a=var.a, b=var.b, common=var.common)  # Valid

    is_equal(C(a=1, b=1.1, common="test"))  # Valid
