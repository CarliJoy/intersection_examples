from typing import Any, Protocol

import pytest
from typing_extensions import override

from intersection_examples import Intersection


@pytest.mark.mypy_testing
def test_function_args():
    class A:
        a: str

    class B:
        b: str

    class C(A, B):
        pass

    class D(A):
        pass

    def func(arg: Intersection[A, B]) -> None:
        return None

    func(C())  # Valid
    func(A())  # E: Argument 1 to "func" has incompatible type "A"; expected "A & B"
    func(B())  # E: Argument 1 to "func" has incompatible type "B"; expected "A & B"
    func(D())  # E: Argument 1 to "func" has incompatible type "D"; expected "A & B"


@pytest.mark.mypy_testing
def test_int_and_str():
    def never_call_me(arg: Intersection[int, str]) -> None:
        pass

    def int_or_str(arg: int | str) -> None:
        never_call_me(
            arg
        )  # E: Argument 1 to "never_call_me" has incompatible type "int | str"; expected "int & str"
        match arg:
            case int():
                print("It's an int")
            case str():
                print("It's a str")
            case _:
                never_call_me(arg)  # E: Statement is unreachable

    int_or_str(1)
    int_or_str("test")


@pytest.mark.mypy_testing
def test_differing_methods():
    class One(Protocol):
        def foo(self, a: int) -> str:
            ...

        def bar(self) -> int:
            ...

    class Two(Protocol):
        def foo(self, a: int) -> int:
            ...

        def bar(self) -> int:
            ...

    class Three(
        One, Two
    ):  # E: Definition of "foo" in base class "One" is incompatible with definition in base class "Two"
        @override
        def bar(self) -> int:
            return 1

    # NOTE: Three is impossible to create because the two methods are incompatible,
    # therefore Intersection type is invalid. Perhaps it should be compatible, but this
    # is most likely out of scope.

    # def func(a: Intersection[One, Two]):
    #     pass

    # func(Three())
