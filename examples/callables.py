from typing import Callable

from intersection_examples import Intersection

test = Intersection[Callable[[int], int], Callable[[int], str]]
print(test.__call__)
print(test.must_subclass)
