from intersection_examples import IntersectionOp5 as Intersection


class A:
    def foo(self, x: str) -> str:
        ...


class B:
    def foo(self, x: int) -> int:
        ...


test = Intersection[A, B]
print(test)
print(test.foo)
