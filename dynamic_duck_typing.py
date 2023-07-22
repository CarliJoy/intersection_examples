import dataclasses
from typing import Protocol, TypeVar, Any, cast

from basedtyping import Intersection
from typing_extensions import reveal_type


T = TypeVar("T")


class EnhancedClass(Protocol):
    def foobar(self, bar: int) -> str:
        ...


def add_function(obj: T) -> Intersection[T, EnhancedClass]:
    def foobar(self: T, bar: int) -> str:
        return f"{self} ({bar})"

    new = cast(Intersection[T, EnhancedClass], obj)
    new.foobar = foobar
    return new



@dataclasses.dataclass
class X:
    bar: str


XEnhanched = add_function(X(bar="foo"))

reveal_type(XEnhanched)
reveal_type(XEnhanched.bar)
reveal_type(XEnhanched.foobar)

class YEnhanced:
    bar: str
    def foobar(self, bar: Intersection[T, EnhancedClass]) -> str:
        return ""


y_enhanced=YEnhanced()
