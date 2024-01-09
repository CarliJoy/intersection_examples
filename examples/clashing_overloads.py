from intersection_examples import IntersectionOp5 as Intersection


class A:
    def foo(self, x: str) -> str:
        ...


class C:
    def foo(self, x: str) -> int:
        ...


test = Intersection[A, C]
