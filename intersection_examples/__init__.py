__all__ = ["Intersection", "get_type_hints"]

from typing import Any, get_args, get_origin
from typing import get_type_hints as get_type_hints_old

from basedtyping import Intersection


def get_type_hints(
    obj: Any,
    globalns: Any | None = None,
    localns: Any | None = None,
    include_extras: bool = False,
) -> dict[str, Any]:
    if get_origin(obj) == Intersection:
        args = get_args(obj)
        new_type_hints = {}
        for arg in args:
            new_type_hints.update(get_type_hints(arg))
        return new_type_hints
    else:
        return get_type_hints_old(
            obj, globalns=globalns, localns=localns, include_extras=include_extras
        )
