from typing import Any

from intersection_examples import Intersection


class A:
    def foo(self) -> int:
        ...


test_new = Intersection[A, Any]
print(test_new)
print("foo", test_new.foo)
print("x", test_new.x)
print()
test_new = Intersection[Any, A]
print(test_new)
print("foo", test_new.foo)
print("x", test_new.x)
