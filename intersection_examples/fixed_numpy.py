from typing import Literal, Protocol, TypeVar, cast

import numpy as np


class FiveLength(Protocol):
    def __len__(self) -> Literal[5]:
        ...


T = TypeVar("T")


def five_long_item(x: T) -> T & FiveLength:
    assert len(x) == 5
    return cast(T & FiveLength, x)


out = five_long_item(np.zeros(5))
len(out)  # length is now fixed
