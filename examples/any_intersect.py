from typing import Any

from intersection_examples import Intersection


class A:
    def foo(self) -> int:
        ...


test = Intersection[A, Any]
print(test)
print("foo", test.foo)
print("x", test.x)
print(test.must_subclass)
print()
test = Intersection[Any, A]
print(test)
print("foo", test.foo)
print("x", test.x)
print(test.must_subclass)
