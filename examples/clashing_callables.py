from typing import Callable

from intersection_examples import IntersectionOp5 as Intersection

test = Intersection[Callable[[int], int], Callable[[int], str]]
