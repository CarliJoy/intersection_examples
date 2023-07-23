**⚠️ NOTE: This is document is currently edited until this line is removed!**

Specification
=============

Theoretical Definition
----------------------
In type theory, an intersection type can be allocated to values that can be assigned both the type σ and the type τ.
This value can be given the intersection type σ ∩ τ in an intersection type system [WIKI1]_.
This means by using an intersection type constructor ( ∩ ) it is possible to assign multiple types to a single term.
In particular, if a term M can be assigned both the type σ and the type τ, then M be assigned the intersection type σ ∩ τ (and vice versa) [WIKI2]_.

In other words specific to Python:
``Intersection`` is a typing composition operator similar like `Union`.
In order for ``Target`` to be a valid (sub)type of ``Union[T1, T2, Tn]``, ``Target`` must by a (sub)type of **any** ``Tn``.
In contrary in order for `Target` to by a valid (sub)type of ``Intersection[T1, T2, Tn]``, ``Target`` must by a (sub)type of **all** ``Tn``.

Python type system know concrete types as well as types defining interfaces (protocols).
Furthermore python is a dynamically language with a gradual typing and language base types that behave different from normal classes.
This could create a lot of ambiguities therefore the following rules are defined for the intersection type.
Some of this rules were already defined `PEP 483`_ and were discussed in the further development of this PEP.

Order
-----
As for Unions the Order of elements of a Intersection does not matter.

Basic Reductions
----------------
In order for the following rules to work correctly the following reduction have to be applied to Intersections first:

- Nested Intersection shall be flattened, i.e ``Intersection[A, Intersection[B, C]] == Intersection[A, B, C]``
- If a (concrete or protocol) type ``A`` is a subtype of ``B``, ``A`` shall be removed from the Intersection
- If a protocol ``BP`` defines **all** methods and properties of a protocol ``AP``, ``AP`` shall be removed from the Intersection
- An Intersection with only one element shall be normalized to the element.


``Any`` Reduction
-----------------
As `PEP 483`_ already suggested: ``Any`` shall be removed from an ``Intersection``, i.e. ``Intersection[A, B, Any] == Intersection[A, B]``.

% This is only a suggestion and needs to be discussed and decided in https://github.com/CarliJoy/intersection_examples/issues/1
% Once it was finally decided the discussion and arguments should be summarized here.


``Never`` Evaluation
--------------------
An Intersection that contains either two classes that are a or are a subclass of two different `internal base classes <https://docs.python.org/3/library/stdtypes.html>`_ shall evaluate to ``Never``.

There are concrete types that can't be subclassed, they are
 - a class marked with ``typing.final`` `[doc] <https://docs.python.org/3/library/typing.html#typing.final>`_
 - ``typing.Never`` and ``typing.NoReturn`` also called `bottom type <https://en.wikipedia.org/wiki/Bottom_type>`_
 - ``None``



The reasoning behind this is that these types can't be subtyped and shouldn't be
dynamically extended.

::

    from typing import TypeVar, reveal_type, Intersection
        from typing import TypeVar, reveal_type, Intersection

    T = TypeVar("T")

    class Enhanced:
        is_great: bool


    def enhance(cls: type[T]) -> type[Intersection[T, Enhanced]]:
        class New(cls, Enhanced):
            ...

        return New

    reveal_type(enhance(str))  # okay
    reveal_type(enhance(None))  # raises a TypeError
    T = TypeVar("T")

    class Enhanced:
        is_great: bool


    def enhance(cls: type[T]) -> type[Intersection[T, Enhanced]]:
        class New(cls, Enhanced):
            ...

        return New

    reveal_type(enhance(str)) # okay
    reveal_type(enhance(None)) # raises a TypeError

# TODO continue here
Old:....

The specific rules for intersections have been already defined in `PEP 483 <https://peps.python.org/pep-0483/#fundamental-building-blocks>`_  they are repeated here:

* The order of the arguments doesn't matter. Nested intersections are flattened, e.g. ``Intersection[int, Intersection[float, str]] == Intersection[int, float, str]``.
* An intersection of fewer types is a supertype of an intersection of
  more types, e.g. ``Intersection[int, str]`` is a supertype
  of ``Intersection[int, float, str]``.
* An intersection of one argument is just that argument,
  e.g. ``Intersection[int]`` is ``int``.
* When argument have a subtype relationship, the more specific type
  survives, e.g. ``Intersection[str, Employee, Manager]`` is
  ``Intersection[str, Manager]``.
*  ``Intersection[]`` is illegal, so is ``Intersection[()]``.
* Corollary: ``Any`` disappears from the argument list, e.g.
  ``Intersection[int, str, Any] == Intersection[int, str]``.
  ``Intersection[Any, object]`` is ``object``.
* The interaction between ``Intersection`` and ``Union`` is complex but
  should be no surprise if you understand the interaction between
  intersections and unions of regular sets (note that sets of types can be
  infinite in size, since there is no limit on the number
  of new subclasses).

Syntax
------

An intersection of types `A` and `B` could either be defined via `Intersection[A, B]` or using the `&` operator as `A & B`.

The instance check of an intersection between concrete types is determined by their method resolution order. For instance:

::

    from typing import Intersection


    class A:
        ...

    class B:
        ...

    class C(A, B):
        ...

    # valid since C is a subtype of all intersected types
    x: Intersection[A, B] = C()

    # invalid since the subtype B is missing
    x: Intersection[A, B] = A()

However, this does not hold for protocols or generics.

Subtyping
---------
As it is not possible to create subtypes of Unions, it is also not possible to create subtypes of Intersections.e

Assignability
-------------

Type checks don’t error on type assignment but they do error when you try to assign a value to the
variable that was just annotated.

::

    # This is invalid since str and float don't intersect
    # but the error doesn't show on Intersection
    x: str & float
    # rather it only shows here when you try to actually assign a variable to x
    x = 3

    # same here - this doesn't fail here
    def foo(x: str & float):
        ...

    # but does fail here
    foo(3)


TODO: Structural type of Intersection[A, B]?
—------------------------------------------

`isinstance` and `issubclass`
-----------------------------

Similarly to union types (see PEP-604), the new syntax should be valid to use in `isinstance` and `issubclass` calls, as long as the intersected types are valid arguments to `isinstance` and `issubclass`.

::

    class A: ...
    class B: ...
    class C(A, B): ...

    # Valid
    isinstance(C(), A & B)
    # Invalid
    isinstance([], list[A] & list[B])

    # Valid
    issubclass(C, A & B)
    # Invalid
    issubclass(list[C], list[A] & list[B])

The `isinstance` or `issubclass` check for an Intersection is equal to the combined checks of all arguments passed:

::

    assert isinstance(val, A & B) == isinstance(val, A) and isinstance(val, B)
    assert issubclass(val, A & B) == issubclass(val, A) and issubclass(val, B)

However the above only applies to concrete types, not Protocols. When performing an `isinstance` or `issubclass` check
for an Intersection of protocol types, `isinstance` and `issubclass` checks for equivalence to the union of all attributes and
methods of the object passed in.

::

  from typing import Protocol, overload


  class ProtoOne(Protocol):
    a: int
    c: Exception

    def foo(self, x: int) -> bool:
      ...

  class ProtoTwo(Protocol):
    a: str
    b: float

    def foo(self, x: str) -> str:
      ...

  class IntersectionOneTwo(Protocol):
    a: str | int
    b: float
    c: Exception

    @overload
    def foo(self, x: int) -> bool:
      ...

    @overload
    def foo(self, x: str) -> str:
      ...

    assert isinstance(val, ProtoOne & ProtoTwo) == isinstance(val, IntersectionOneTwo)
    assert issubclass(val, ProtoOne & ProtoTwo) == issubclass(val, IntersectionOneTwo)

The reason for the difference in behaviour between concrete and protocol types here is the following.
The logic for checking concrete types works by checking that the method resolution order of all objects
passed are equivalent. However, this is not possible to do for protocols. Consequently, it is necessary
to check that the combined behaviour of objects' attributes and methods.

.. [WIKI1] https://en.wikipedia.org/wiki/Intersection_type
.. [WIKI2] https://en.wikipedia.org/wiki/Intersection_type_discipline

.. _PEP 483: https://peps.python.org/pep-0483/#fundamental-building-blocks
