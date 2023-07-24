import typing

from basedtyping import Intersection


@typing.overload
def foo(val: int) -> str:
    ...


@typing.overload
def foo(val: float) -> bytes:
    ...


def foo(val: float | int) -> str | bytes:
    if isinstance(val, int):
        return str(val)
    return str(val).encode()


val_int: int = 1
val_float: float = 1.3


def get_func() -> typing.Callable[[int], str] | typing.Callable[[float], bytes]:
    return foo  # no type error


def get_func_intersection() -> (
    Intersection[typing.Callable[[int], str], typing.Callable[[float], bytes]]
):
    return foo  # no type error


# Allowing both results to be correct seems strange?

typing.reveal_type(foo(val_int))
typing.reveal_type(foo(val_float))
typing.reveal_type(get_func()(val_int))  # str | bytes
typing.reveal_type(get_func_intersection()(val_int))  # str


class A:
    def foo(self, val: int) -> str:
        return str(val)


class B:
    def foo(self, val: float) -> bytes:
        return str(val).encode()


def get_intersection() -> Intersection[A, B]:
    class Intersected:
        @typing.overload
        def foo(self, val: int) -> str:
            ...

        @typing.overload
        def foo(self, val: float) -> bytes:
            ...

        def foo(self, val: float | int) -> str | bytes:
            if isinstance(val, int):
                return str(val)
            return str(val).encode()

    return Intersected  # got type error?


typing.reveal_type(get_intersection().foo(val_int))  # str, as expected
