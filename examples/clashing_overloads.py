from intersection_examples import Intersection


class A:
    def foo(self, x: str) -> str:
        ...


class C:
    def foo(self, x: str) -> int:
        ...


test = Intersection[A, C]
print(test.foo)
print(test.must_subclass)
