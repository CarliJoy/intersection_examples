__all__ = ["Intersection"]
"""
The idea of this is to simulate the return type of an intersection of two classes.
This currently only works for direct methods or attributes of the class.
"""

from inspect import Signature, signature
from typing import Any


def signatures_compatible(s1: Signature, s2: Signature) -> bool:
    # TODO: Test for non overlapping signatures
    return s1 == s2


excluded_methods = ["__class__", "__init_subclass__", "__subclasshook__", "__new__"]
get_attribute_excludes = ["__intersects__", "_test_lsp"]


class Intersection:
    __intersects__: set[type[object]]

    def __init__(self, *intersects: type[object]) -> None:
        self.__intersects__ = set(reversed(intersects))
        self._test_lsp()

    def __class_getitem__(cls, key):
        return cls(*key)

    def _test_lsp(self):
        intersected_attrs: dict[str, type] = {}
        signatures: dict[str, Signature] = {}
        for i in self.__intersects__:
            # Resolve basic annotations, ensuring no clashes
            for annotation_name, annotation_type in i.__annotations__.items():
                if annotation_name in intersected_attrs:
                    if annotation_type != intersected_attrs[annotation_name]:
                        raise TypeError("LSP Violation")
                else:
                    intersected_attrs[annotation_name] = annotation_type

            for method_name in dir(i):
                method = getattr(i, method_name)
                if callable(method) and method_name not in excluded_methods:
                    sig = signature(method)
                    if method_name in signatures:
                        if not signatures_compatible(sig, signatures[method_name]):
                            raise TypeError(
                                f"Signatures {sig} and {signatures[method_name]} not compatible"
                            )
                    else:
                        signatures[method_name] = sig

    def __repr__(self) -> str:
        attrs = list(i.__name__ for i in self.__intersects__)
        return " & ".join(attrs)

    def __getattribute__(self, name: str):
        if name in get_attribute_excludes:
            return super().__getattribute__(name)
        for i in self.__intersects__:
            if hasattr(i, name) and callable(getattr(i, name)):
                return signature(getattr(i, name))
            elif name in i.__annotations__:
                return i.__annotations__[name]

        if Any in self.__intersects__:
            return Any
        raise AttributeError(f"Attribute not found on type {self}")
