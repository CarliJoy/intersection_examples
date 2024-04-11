from intersection_examples import Intersection


class A:
    test: int

    def foo(self, x: str) -> str:
        ...


class B:
    test: int

    def foo(self, x: int) -> int:
        ...


test = Intersection[A, B]
print(test)
print(test.test)
print(test.foo)
print(test.must_subclass)
print()
test = Intersection[B, A]
print(test)
print(test.test)
print(test.foo)
print(test.must_subclass)
