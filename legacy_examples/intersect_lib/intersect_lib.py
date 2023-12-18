import random

from basedtyping import Intersection

# Here this is assumed to be an external library


class A:
    def randomiser(self):
        return random.random()


def class_merger(cls: type[T], name: str) -> type[Intersection[T, A]]:
    return type(name, (cls, A), {})
