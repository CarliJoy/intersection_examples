**⚠️ NOTE: This is document is work in progress, help wanted, see https://github.com/CarliJoy/intersection_examples/blob/main/README.md**


This following PEP was written originally on the PyCON US by Kevin Millikin (@kmillikin) and Sergei
Lebedev (@superbobry).
The specification was adopted on a Sprint at Europython -> be aware it is known to be unsound and
overly complex at the moment.

See also `The General Status Issues <https://github.com/CarliJoy/intersection_examples/issues/8>`_.

PEP: 9999
Title: Intersection types
Author: TODO
Sponsor: TODO
Status: Draft
Type: Standards Track
Content-Type: text/x-rst
Created: xxx
Python-Version: 3.12
Post-History:

Abstract
========

This PEP proposes the addition of intersection types.
They are denoted as `A & B` or `Intersection[A, B]` and they describe values that have both types A
and B.
Intersection types are a complementary concept to union types introduced in PEP-484.

The primary use cases for intersection types include:

- mixin classes, which require certain APIs to be available in the class hierarchy;
- wrapper types, which add information to the original type without monkey patching;
- combining multiple protocols into a single structural type;
- ad-hoc merging of TypedDict types; and
- type narrowing in control flow.

This PEP outlines the syntax, subtyping rules, assignability, isinstance and issubclass usage, and
other aspects related to intersection types.[A short (~200 word) description of the technical issue
being addressed.]

Introduction
============

PEP-484 introduced the concept of a union type, written `Union[A, B]` which describes values of
either type `A` or type `B`.
Intersection types provide a different (complementary) way of combining types.
The type `A & B` describes values which have both type `A` and type `B`.

For example,

::

    class A: ...
    class B: ...
    class C(A, B): ...
    class D(A): ...

    def f(value: A & B): ...


here it is valid to call `f` on an instance of `C`, but invalid to call it with instances of `A`,
`B` or `D`.

Motivation
==========

This section motivates intersection types using examples that cannot be easily solved with current
typing constructs.
[Clearly explain why the existing language specification is inadequate to address the problem that
the PEP solves.]


Mixins
------

Mixin classes often have to assume a certain API, which is not implemented by the mixin, but needs
to be available in the class hierarchy where the mixin is used.
For example,

::

    class LoginRequiredMixin:
        def dispatch(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
        	     ...
            return super().dispatch(request, *args, **kwargs)

The `LoginRequiredMixin` is designed to be used with the `View` base class which defines the
`dispatch` method.
Intersection types allow expressing that directly via

::

    class LoginRequiredMixin:
        def dispatch(self: LoginRequiredMixin & View, request, *args, **kwargs): ...

Source: https://docs.djangoproject.com/en/3.2/topics/auth/default/#django.contrib.auth.mixins.LoginRequiredMixin


Wrappers
--------

Another use case for intersection would be the creation of wrapper types that add more information
to the original type without monkey patching

::

    from typing import Type, TypeVar, Generic

    _T = TypeVar("_T")

    class Wrapper(Generic[_T]):
        wrap: Type[_T]
        enhanced: bool = True

        def __init__(self, cls: Type[_T]) -> None:
            self.wrap = cls

        def __call__(self, *args, **kwargs): ...

    def enhance(cls:  Type[_T]) -> Type[_T] & Wrapper[_T]:
        return Wrapper(cls)

    class X:
        ...

    EnhanceX = enhance(X)

    reveal_type(EnhanceX)            # Type[X] & Wrapper[X]
    reveal_type(EnhanceX.enhanced)   # bool


Protocols
---------

Intersection types allow to succinctly combine multiple protocols (see PEP-544) into a single
structural type.
For example, instead of

::

    from collections.abc import Container, Iterable
    from typing import Protocol, TypeVar

    T = TypeVar(“T”)

    class IterableContainer(Iterable[T], Container[T], Protocol):
        ...

    def assert_in(target: T, it: IterableContainer[T]) -> bool:
        if item not in it:
            raise AssertionError(f“{target} does not occur in {‘, ‘.join(map(str, it))}”)

users could drop the `IterableContainer` class and instead annotate `it` as
`Iterable[T] & Container[T]`.

Source: https://github.com/python/typing/issues/18

TypedDict
---------

PEP-589 introduced `TypedDict`, a way to define precise types for dictionaries with a fixed set of
keys.
Multiple `TypedDict` types could be merged into a single `TypedDict` type through subclassing.
For example,

::

    from typing import TypedDict

    class Movie(TypedDict):
        name: str
        year: int

    class BookBasedMovie(Movie):
        based_on: str

With intersection types, `TypedDict` types no longer need to be inherited, and can be combined in
ad-hoc way::

    class BookBased(TypedDict):
        based_on: str

    BookBasedMovie = Movie & BookBased


Type narrowing in control flow
------------------------------

Type checkers employ type narrowing for certain conditionally executed code as described in PEP-647.
An `isinstance` check, for example, can be used to narrow the static type of its first argument

::

    x: A
    if isinstance(x, B):
        f(x)

In the call to `f`, `x` is known to have both static types `A` and `B`.
If `B` is a subtype of `A`
then that static type is the same as `B`.
But of course, `A` and `B` do not necessarily have any
subtype relationship.
With intersection types the static type of `x` can be exactly represented as `A & B` and the
programmer can write the type annotation for `f` accordingly:

::

    def f(x: A & B): ...

Type checkers actually do implement some form of intersection types internally to support type
narrowing.
This can be observed using a facility like `reveal_type` in place of the call to `f`
above.
For instance, mypy will display `<subclass of "A" and "B">` and pyright will display
`<subclass of A and B>`.
Intersection types allow programmers to write this type annotation, even
including more complicated cases such as:

::

    y: Union[A, B]
    if isinstance(y, C):
        g(y)

At the call to `g`, `y` has the static type `Union[A, B] & C`.
(Both mypy and pyright
"distribute" the union over the intersection, displaying `Union[<subclass of "A" and "C">, <subclass
of "B" and "C">]` and `<subclass of A and C> | <subclass of B and C>` respectively.)

Theory
======

Theoretical Definition
----------------------
In type theory, an intersection type can be allocated to values that can be assigned both the type σ
and the type τ.
This value can be given the intersection type σ ∩ τ in an intersection type system [WIKI1]_.
This means by using an intersection type constructor ( ∩ ) it is possible to assign multiple types
to a single term.
In particular, if a term M can be assigned both the type σ and the type τ, then M be assigned the
intersection type σ ∩ τ (and vice versa) [WIKI2]_.

In other words specific to Python:
``Intersection`` is a typing composition operator similar like `Union`.
In order for ``Target`` to be a valid (sub)type of ``Union[T1, T2, Tn]``, ``Target`` must by a (sub)type of **any** ``Tn``.
In contrary in order for `Target` to by a valid (sub)type of ``Intersection[T1, T2, Tn]``, ``Target`` must by a (sub)type of **all** ``Tn``.

Python type system know concrete types as well as types defining interfaces (protocols).
Furthermore python is a dynamically language with a gradual typing and language base types that
behave different from normal classes.
This could create a lot of ambiguities therefore the following rules are defined for the
intersection type.
Some of this rules were already defined `PEP 483`_ and were discussed in the further development of
this PEP.

Intuition based on sets
-----------------------

A simple way to understand Python static types is to think of them as describing sets of runtime
objects.
The type `str` describes the set of all Python strings.
Likewise if `C` is a class then the type `C` describes the set of all instances of `C` including
instances of its subclasses.
A type annotation on a variable declares that at runtime the value of the variable will be an
element of the set that the annotation describes.
(Which is not necessarily true because the type system allows conversions both to and from the type
`Any` without any runtime checks.)

The rules for subtyping sketched in PEP-483 are intended to ensure that if a type `B` is a subtype
of a type `A`, then the set of values described by `B` is always a subset of the set of values
described by `A`.

Union types describe the union of the sets of values of their components.
For example, `Union[str,C]` describes the set containing all Python strings and all instances of `C`
including instances of its subclasses.
A type annotation `Union[str,C]` on a variable declares that at runtime the value of the variable
will either be a string or an instance of `C` (or possibly both).
This is why the operations that a typechecker allows on such a value are only the operations that
are allowed on both strings and instances of `C`.
The only safe things to do with such a value are the things that are allowed for all components of
the union, that is the _intersection_ of those things to do.

Similarly, intersection types describe the intersection of the sets of values of their components.
For example, `str & C` describes the set containing all Python objects that are both
elements of the set of strings and elements of the set of instances of `C` including instances of
its subclasses.
Notice that this does not require that `C` is a subclass of `str` or vice versa.
There may be classes that are themselves subclasses of both `str` and `C` and so their instances
will be in the intersection.
There may even be several such subclasses of `str` and `C` that are not necessarily subclass-related
to each other.
And the intersection may be empty if there are no Python objects that are both in the set of strings
and the set of instances of `C`.

The operations that a typechecker allows on an intersection type are the operations that are allowed
on any component.
That is, the _union_ of those operations.

A subtype of an intersection type should describe a subset of the set of objects described by the
intersection type.
Namely, this means that it should also be a subtype of all of the components of the intersection (it
cannot possibly contain an element that is not contained in each of the components).
An intersection type itself is a subtype of each of its components, because it describes a subset of
the sets described by each component.

This set-based intuition extends to other types besides class instances.
For example, we can form an intersection of a union type like `(A | B) & C`.
The first component of the intersection is the set containing all instances of `A` and all instances
of `B`.
The intersection with the set containing all instances of `C` describes all the Python objects that
are both instances of the union (either `A` or `B`) and also instances of `C`.
This set-based intuition justifies distributing the union over the intersection (as shown by mypy
and pyright above) and recognizing that it describes the same set of objects as `A & C | B & C`.


Specification
=============

Syntax
------

An intersection of types `A` and `B` should be defined using the operator `A & B`, or
`Intersection[A, B]` when programmatically generating intersections.


Order and Emptiness
-------------------
As for unions the order of elements of an intersection does not matter.


`isinstance` and `issubclass`
-----------------------------

Similarly to union types (see PEP-604), the new syntax should be valid to use in ``isinstance`` and
``issubclass`` calls, as long as the intersected types are valid arguments to ``isinstance`` and
``issubclass``.

The `isinstance` or `issubclass` check for an intersection is equal to the combined checks of all
arguments passed:

::

    class A: ...
    class B: ...

    assert isinstance(val, A & B) == isinstance(val, A) and isinstance(val, B)
    assert issubclass(val, A & B) == issubclass(val, A) and issubclass(val, B)


It shall be noted, that following the `PEP 544 <https://peps.python.org/pep-0544/#support-isinstance-checks-by-default>`_ about the rejected default ``isinstance`` check:
If any Protocol within the intersection isn't marked with ``typing.runtime_checkable``,
``isinstance`` will raise a TypeError.


So one possibility to fulfill an intersection is for a class to be a child of all intersected classes.

::
    class C(A, B): ...

    isinstance(C(), A & B)  # True
    issubclass(C, A & B)  # True

Basic Reductions
----------------
In order for the following rules intended for type checkers to work correctly the following
reduction have to be applied to Intersections first:

- Nested intersections shall be flattened, i.e ``Intersection[A, Intersection[B, C]] ==
  Intersection[A, B, C]``
- If a (concrete or protocol) type ``A`` is a subtype of ``B``, ``A`` shall be removed from the
  intersection
- If a protocol ``BP`` defines **all** methods and properties of a protocol ``AP``, ``AP`` shall be
  removed from the intersection
- If the concrete class ``A`` fulfils the Protocol ``AP``, ``AP`` shall be removed from the
  intersection
- An intersection with only one element shall be normalized to the element.


``Any`` Reduction
-----------------
As `PEP 483`_ already suggested: ``Any`` shall be removed from an ``Intersection``, i.e.
``Intersection[A, B, Any] == Intersection[A, B]``.

% This is only a suggestion and needs to be discussed and decided in https://github.com/CarliJoy/intersection_examples/issues/1
% Once it was finally decided the discussion and arguments should be summarized here.


``Never`` Evaluation
--------------------
An intersection that contains either two classes that are a or are a subclass of two different `internal base classes <https://docs.python.org/3/library/stdtypes.html>`_ shall evaluate to ``Never``.
Examples for internal baseclasses are:

- BaseException
- bool
- bytearray
- bytes
- complex
- dict
- float
- frozenset
- int
- list
- memoryview
- range
- set
- str
- tuple
- type

There are concrete types that can't be subclassed, they are
 - a class marked with ``typing.final`` `[doc] <https://docs.python.org/3/library/typing.html#typing.final>`_
 - ``typing.Never`` and ``typing.NoReturn`` also called `bottom type <https://en.wikipedia.org/wiki/Bottom_type>`_
 - ``None``

If such a type is used within an intersection this intersection shall evaluate to ``Never``.

The reasoning behind this is that these types can't be subtyped and shouldn't be dynamically
extended.
Doing this early prevents issues during subtyping or assignments checks.

::

    from typing import TypeVar, reveal_type

    T = TypeVar("T")

    class Enhanced:
        is_great: bool


    def enhance(cls: type[T]) -> type[T & Enhanced]:
        class New(cls, Enhanced):
            ...

        return New

    reveal_type(enhance(str))  # okay
    reveal_type(enhance(None))  # raises a TypeError on runtime, should be flagged by TypeCheckers

It is important to note that once a type checker evaluated anything to ``Never`` within an
intersection it can stop further evaluations an return ``Never``.
This way a lot of edge cases by mixin types that can't be mixed are handled easily.

Handling Callables
------------------
Every Callable within an intersection shall be treated like a ``def __call__()`` Protocol.

::

    from typing import Protocol, Callable

    MyCallable = Callable[[str, int], float]

    class CallProto:
        def __call__(a: str, b: int) -> float: ...

    # Type Checker should perform the following conversion
    # T & MyCallable => T & CallProto

This way the ``overload`` mechanism described below can be used.


Protocol Reduction
------------------

A type checker shall combine all protocols of an intersection in the following way:

% TODO: Shall this be valid also for ABC?

- Create a new empty protocol ``Merged``
- Cycle over all protocols and their attributes.

  - For each of such attributes do:

    - If: the given attribute does not exist, copy it to ``Merged``
    - Else If: the given already exist in ``Merged`` and is a callable (function/method), mark the
      attribute ``@overloaded`` (if not done already) and add current attribute as ``@overloaded``
      as well
    - Else:

      - If: The attribute in ``Merged`` is a (or multiple) callable(s), convert them to **one**
        ``__call__`` protocol (if multiple callables, with overloads)
      - If: The attribute in ``Merged`` is no union make it one
      - If: Uhe given attribute is a callable and there is already a call protocol in the Union, add
        the given attribute as overload
      - Else: Add the given attribute to the union



Please note for ``@overload`` the sub file rules apply as described in `PEP 484 <https://peps.python.org/pep-0484/#function-method-overloading>`_

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

TypedDicts
----------

If multiple TypedDicts are given within an intersection, their attributes shall be handled as described with ``Protocol`` attributes.

::

    import typing


    class A(typing.TypedDict):
        a: int
        common: str


    class B(typing.TypedDict):
        b: float
        common: bytes


    class Intersected(typing.TypedDict):
        a: int
        b: float
        common: str | bytes


    def is_equal(var: A & B) -> Intersected:  # The two representations are equal
        return var  # no type error

Unions
------

The general set theory applies for handling Unions.
The following rules apply

% TODO Define an alogrithm that shall be used by type checkers
 - ``(A | B) & C = (A & C) | (B & C)``

% see https://github.com/CarliJoy/intersection_examples/issues/3

Assignability
-------------

A type checker validating that a variable can be assigned to an intersection the following should be
done:

 - check that the variable ``issubclass()`` of all concrete classes
 - ensure that the ``Merged`` protocol (see above) fits to the given variable

The differentiation between concrete types (nominal typing) and protocols (structural typing) is
inherent the current Python type system and shall not be changed.

::

    class A:
        ...

    class B:
        ...

    class C(A, B):
        ...

    # valid since C is a subtype of all intersected types
    x: A & B = C()

    # invalid since the subtype B is missing
    x: A & B = A()


Subtyping
---------
As it is not possible to create subtypes of Unions, it is also not possible to create subtypes of
Intersections.

Still a type checker needs to be able to create a virtual type internally when ``A && B`` is used.
As it doesn't know anything about potential MRO of concrete classes (since the order of an
``Intersection`` does not matter), we need a different way of creating types for attributes.
To do so, the type checker shall apply the algorithm described in Protocol Reduction not only to
protocols but to all types given.
The resulting ``Merged`` protocol shall be used internally by the type checker as representation of
the the given ``Intersection`` type for all further checks.

% TODO maybe ``reveal_type`` could accepts a keyword argument, verbose that prints this protocol?

.. [WIKI1] https://en.wikipedia.org/wiki/Intersection_type
.. [WIKI2] https://en.wikipedia.org/wiki/Intersection_type_discipline

.. _PEP 483: https://peps.python.org/pep-0483/#fundamental-building-blocks


How to Teach This
=================

[How to teach users, new and experienced, how to apply the PEP to their work.]


Reference Implementation
========================
[Link to any existing implementation and details about its state, e.g. proof-of-concept.]

https://github.com/Ovsyanka83/type-intersections
https://github.com/KotlinIsland/basedmypy/commit/8990b08f6e3a15bf80597c66343ba2cbe41148bd
