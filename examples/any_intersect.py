from typing import Any

from intersection_examples import Intersection


class A:
    def foo(self) -> int:
        pass


test_new = Intersection[A, Any]
print(test_new)
print(test_new.foo)
print(test_new.x)
