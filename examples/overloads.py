from intersection_examples import Intersection


class A:
    def foo(self, x: str) -> str:
        ...


class B:
    def foo(self, x: int) -> int:
        ...


test = Intersection[A, B]
print(test)
print(test.foo)
print(test.must_subclass)
