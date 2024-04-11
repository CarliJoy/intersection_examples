__all__ = ["Intersection"]
"""
The idea of this is to simulate the return type of an intersection of two classes.
This currently only works for direct methods or attributes of the class.
"""
from inspect import Parameter, Signature, signature as sig_func
from typing import (
    Any,
    Callable,
    Self,
    Sequence,
    cast,
    get_args,
    get_origin,
    get_overloads,
)


excluded_methods = ["__class__", "__init_subclass__", "__subclasshook__", "__new__"]
get_attribute_excludes = [
    "__intersects__",
    "__callables__",
]


def get_possible_methods(method: Callable) -> Sequence[Callable]:
    try:
        overloads = get_overloads(method)
    except:
        overloads = []
    if len(overloads) == 0:
        return [method]
    else:
        return overloads


# Inheritance from Any added to allow type checking to be enabled - attributes of
# this class are unknown to the type checker.
class Intersection(Any):
    __intersects__: list[type[object]]
    __dict__: Any

    def __init__(self, *intersects: type[object]) -> None:
        self.__intersects__ = list(intersects)

    def __new__(cls, *args, **kwargs) -> Self:
        # Workaround to allow inheritance from Any
        return super().__new__(cls)

    def __class_getitem__(cls, key):
        """
        Allows for the generation of an instance of Intersection based on
        a series of types (the expected interface of intersection)
        """
        return cls(*key)

    def __repr__(self) -> str:
        attrs = list(repr(i) for i in self.__intersects__)
        return " & ".join(attrs)

    def __getattribute__(self, name: str):
        """
        Overrides the default behaviour for get attribute,
        now returns the type of the attribute rather than the attribute itself.

        Args:
            name (str): The name of the attribute to obtain

        Raises:
            AttributeError: Attribute not found

        Returns:
            _type_: The type of the attribute requested
        """

        if name in get_attribute_excludes:
            return super().__getattribute__(name)

        for i in self.__intersects__:
            if i == Any:
                return Any
            elif hasattr(i, "__annotations__") and name in i.__annotations__:
                return i.__annotations__[name]
            elif hasattr(i, name):
                try:
                    is_callable = issubclass(cast(Any, get_origin(i)), Callable)
                except:
                    is_callable = False
                if is_callable:
                    params, return_type = get_args(i)
                    return Signature(
                        parameters=[
                            Parameter(name="self", kind=Parameter.POSITIONAL_ONLY)
                        ]
                        + [
                            Parameter(
                                name="param" + str(x),
                                kind=Parameter.POSITIONAL_ONLY,
                                annotation=i,
                            )
                            for x, i in enumerate(params)
                        ],
                        return_annotation=return_type,
                    )
                else:
                    method = getattr(i, name)
                    if callable(method) and name not in excluded_methods:
                        sig_funcs = [sig_func(i) for i in get_possible_methods(method)]
                        if len(sig_funcs) == 1:
                            return sig_funcs[0]
                        else:
                            return (
                                "Overload["
                                + ",".join([format(i) for i in sig_funcs])
                                + "]"
                            )
                    else:
                        return type(method)
            else:
                pass

        raise AttributeError(f"Attribute not found on type {self}")
