from intersection_examples import Intersection


class A:
    def foo(self, x: str) -> str:
        pass


class C:
    def foo(self, x: str) -> int:
        return 1


test = Intersection[A, C]
