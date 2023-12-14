import typing

import pytest

from intersection_examples import Intersection


@pytest.mark.mypy_testing
def test_callables():
    @typing.overload
    def foo(val: int) -> str:
        ...

    @typing.overload
    def foo(val: float) -> bytes:
        ...

    def foo(val: float | int) -> str | bytes:
        if isinstance(val, int):
            return str(val)
        return str(val).encode()

    def get_func() -> typing.Callable[[int], str] | typing.Callable[[float], bytes]:
        return foo  # Valid

    def get_func_intersection() -> (
        Intersection[typing.Callable[[int], str], typing.Callable[[float], bytes]]
    ):
        return foo  # E: Intersection used on callable

    # Allowing both results to be correct seems strange?


# NOTE: I would argue the Intersection of these is equivalent
# to the below, so really we're back to the method problem:
@pytest.mark.mypy_testing
def test_callables_as_protocols():
    @typing.overload
    def foo(val: int) -> str:
        ...

    @typing.overload
    def foo(val: float) -> bytes:
        ...

    def foo(val: float | int) -> str | bytes:
        if isinstance(val, int):
            return str(val)
        return str(val).encode()

    class Inter1(typing.Protocol):
        def __call__(self, a: int) -> str:
            ...

    class Inter2(typing.Protocol):
        def __call__(self, a: float) -> bytes:
            ...

    def get_func() -> Inter1 | Inter2:
        return foo  # Valid

    def get_func_intersection() -> Intersection[Inter1, Inter2]:
        return foo  # E: Incompatible return value type (got overloaded function, expected "Inter1 & Inter2")


@pytest.mark.mypy_testing
def test_protocols():
    class A(typing.Protocol):
        def foo(self, val: int) -> str:
            ...

    class B(typing.Protocol):
        def foo(self, val: float) -> bytes:
            ...

    def get_intersection() -> type[Intersection[A, B]]:
        class Intersected:
            @typing.overload
            def foo(self, val: int) -> str:
                ...

            @typing.overload
            def foo(self, val: float) -> bytes:
                ...

            def foo(self, val: float | int) -> str | bytes:
                if isinstance(val, int):
                    return str(val)
                return str(val).encode()

        return Intersected
