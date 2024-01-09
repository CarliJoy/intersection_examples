from typing import Any

from intersection_examples import IntersectionOp5, IntersectionOp4


class A:
    def foo(self) -> int:
        ...


test_new = IntersectionOp5[A, Any]
print(test_new)
print(test_new.foo)
print(test_new.x)

test_new = IntersectionOp4[A, Any]
print(test_new)
print(test_new.foo)
print(test_new.x)
