__all__ = ["Intersection"]
"""
The idea of this is to simulate the return type of an intersection of two classes.
This currently only works for direct methods or attributes of the class.
"""

from inspect import Signature
from inspect import signature as sig_func
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


def include_sig(new_sig: Signature, existing_sigs: list[Signature]) -> list[Signature]:
    def signatures_compatible(s1: Signature, s2: Signature):
        if s1 == s2:
            return True
        else:
            return s1.parameters != s2.parameters

    for existing_sig in existing_sigs:
        if not signatures_compatible(new_sig, existing_sig):
            raise TypeError(f"Signatures {new_sig} and {existing_sig} not compatible")
    if new_sig in existing_sigs:
        return existing_sigs
    else:
        return existing_sigs + [new_sig]


def include_call(new_call: Callable, existing_calls: list[Callable]) -> list[Callable]:
    def callables_compatible(s1: Callable, s2: Callable):
        if s1 == s2:
            return True
        else:
            params1, _ = get_args(s1)
            params2, _ = get_args(s2)
            return params1 != params2

    for existing_call in existing_calls:
        if not callables_compatible(new_call, existing_call):
            raise TypeError(f"Callables {new_call} and {existing_call} not compatible")
    if new_call in existing_calls:
        return existing_calls
    else:
        return existing_calls + [new_call]


excluded_methods = ["__class__", "__init_subclass__", "__subclasshook__", "__new__"]
get_attribute_excludes = [
    "__intersects__",
    "_get_annotations",
    "_get_signatures",
    "__signatures__",
    "__inter_annotations__",
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


base_types = (
    int,
    float,
    str,
    bytes,
    bytearray,
    bool,
    type,
    BaseException,
    set,
    list,
    tuple,
    range,
    memoryview,
    dict,
    frozenset,
    complex,
)


class Intersection(Any):
    __intersects__: set[type[object]]
    __signatures__: dict[str, list[Signature]]
    __callables__: Sequence[Callable]
    __inter_annotations__: dict[str, type]
    __dict__: Any

    def __init__(self, *intersects: type[object]) -> None:
        self.__intersects__ = set(reversed(intersects))
        for i in self.__intersects__:
            if not hasattr(i, "mro"):
                raise ValueError(f"mro not found for {i}")
            for base_type in base_types:
                if base_type in i.mro():
                    raise TypeError(
                        f"Type {i} found to derive from base type {base_type}"
                    )
        self.__signatures__, self.__callables__ = self._get_signatures()
        self.__inter_annotations__ = self._get_annotations()

    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls)

    def __class_getitem__(cls, key):
        return cls(*key)

    def _get_annotations(self) -> dict[str, type]:
        intersected_attrs: dict[str, type] = {}
        for i in self.__intersects__:
            # Resolve basic annotations, ensuring no clashes
            if hasattr(i, "__annotations__"):
                for annotation_name, annotation_type in i.__annotations__.items():
                    if annotation_name in intersected_attrs:
                        if annotation_type != intersected_attrs[annotation_name]:
                            raise TypeError(
                                f"Attribute {annotation_name} has type clash on {annotation_type} vs {intersected_attrs[annotation_name]}"
                            )
                    else:
                        intersected_attrs[annotation_name] = annotation_type
        return intersected_attrs

    def _get_signatures(self) -> tuple[dict[str, list[Signature]], list[Callable]]:
        signatures: dict[str, list[Signature]] = {}
        callables: list[Callable] = []
        for i in self.__intersects__:
            try:
                is_callable = issubclass(cast(Any, get_origin(i)), Callable)
            except:
                is_callable = False

            if is_callable:
                callables = include_call(i, callables)
            else:
                for method_name in dir(i):
                    method = getattr(i, method_name)
                    if callable(method) and method_name not in excluded_methods:
                        new_sigs = [sig_func(i) for i in get_possible_methods(method)]
                        for new_sig in new_sigs:
                            if method_name in signatures:
                                signatures[method_name] = include_sig(
                                    new_sig, signatures[method_name]
                                )
                            else:
                                signatures[method_name] = [new_sig]

        return signatures, callables

    def __repr__(self) -> str:
        attrs = list(repr(i) for i in self.__intersects__)
        return " & ".join(attrs)

    def __getattribute__(self, name: str):
        if name in get_attribute_excludes:
            return super().__getattribute__(name)
        if name in self.__inter_annotations__:
            return self.__inter_annotations__[name]

        if name in self.__signatures__:
            possible_signatures = {format(sig) for sig in self.__signatures__[name]}
        else:
            possible_signatures = set()

        if len(possible_signatures) == 1:
            return next(iter(possible_signatures))
        elif len(possible_signatures) > 1:
            return "Overload[" + ", ".join(possible_signatures) + "]"

        if Any in self.__intersects__:
            return Any
        raise AttributeError(f"Attribute not found on type {self}")
