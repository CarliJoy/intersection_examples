from typing import Any, Generic, Protocol, TypeVar

from typing_extensions import reveal_type

_T = TypeVar("_T")


class WrapperProtocol(Protocol):
    enhanced: bool


class Wrapper(Generic[_T]):
    wrap: _T
    enhanced: bool = True

    def __init__(self, wrapped: _T) -> None:
        self.wrap = wrapped

    def __getattr__(self, item) -> Any:
        return getattr(self.wrap, item)


class XProtocol(Protocol):
    base: str


class Combined(WrapperProtocol, XProtocol, Protocol):
    ...


def enhance(obj: _T) -> Combined:
    return Wrapper(obj)  # type: ignore


class X:
    base: str = "bar"


EnhanceX = enhance(X)

reveal_type(EnhanceX)  # Type[X] & Wrapper[X]
reveal_type(EnhanceX.enhanced)  # bool
reveal_type(EnhanceX.base)  # str
