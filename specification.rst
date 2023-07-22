Specification
=============

[Describe the syntax and semantics of any new language feature.]
Some basic rules forrulesThe specific rules for intersections have been already defined in `PEP 483 <https://peps.python.org/pep-0483/#fundamental-building-blocks>`_  they are repeated here:

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

    class C(B):
        ...

    # valid since mro of A and B is the same
    x: Intersection[A, B] = A()

    # invalid since mro of A and C is different
    x: Intersection[A, C] = A()

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

However the above only applies to concrete types, not Protocols.
The `isinsnstance` or `issubclass` check for an Intersection is equal to the and combined checks of all arguments::

    assert isinstance(val, A & B) == isinstance(val, A) and isinstance(val, B)
    assert issubclass(val, A & B) == issubclass(val, A) and issubclass(val, B)
