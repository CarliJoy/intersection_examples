# Based on : https://stackoverflow.com/questions/70698000/workaround-for-lack-of-intersection-types-with-python-generics

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from basedtyping import Intersection


class Animal(ABC):
    @abstractmethod
    def name(self) -> str:
        ...


class CanFly(Animal):
    @abstractmethod
    def fly(self) -> None:
        ...


class CanSwim(Animal):
    @abstractmethod
    def swim(self) -> None:
        ...


class Bird(CanFly):
    def fly(self) -> None:
        print("flap wings")


class Penguin(Bird, CanSwim):
    def name(self) -> str:
        return "penguin"

    def swim(self) -> None:
        print("paddle flippers")


T = TypeVar("T", bound=Animal, contravariant=True)


class Petter(Generic[T], ABC):
    @abstractmethod
    def pet(self, a: T) -> None:
        ...


class CanFlyAndSwimPetter(Petter[Intersection[CanFly, CanSwim]]):
    def pet(self, a: Intersection[CanFly, CanSwim]):
        a.name()
        a.fly()
        a.swim()


CanFlyAndSwimPetter().pet(Penguin())
