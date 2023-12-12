import pytest

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

    def func1(arg: Intersection[A, B]) -> None:
        return None

    func1(C())  # Valid
    func1(A())  # E: Argument 1 to "func1" has incompatible type "A"; expected "A & B"
    func1(B())  # E: Argument 1 to "func1" has incompatible type "B"; expected "A & B"
    func1(D())  # E: Argument 1 to "func1" has incompatible type "D"; expected "A & B"
