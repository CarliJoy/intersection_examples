PEP: <REQUIRED: pep number>
Title: Intersection Type
Author: <REQUIRED: list of authors' real names and optionally, email addrs>
Sponsor: <real name of sponsor>
PEP-Delegate: <PEP delegate's real name>
Discussions-To: <REQUIRED: URL of current canonical discussion thread>
Status: Draft
Type: Standards Track
Topic: Typing
Requires: <pep numbers>
Created: <date created on, in dd-mmm-yyyy format>
Python-Version: <version number>
Post-History: <REQUIRED: dates, in dd-mmm-yyyy format, and corresponding links to PEP discussion threads>
Resolution: <url>


Abstract
========

This PEP proposes the addition of intersection types.
They are denoted as ``A & B`` or ``Intersection[A, B]`` and as a
type expression they express a requirement that a value is consistent with
multiple types, here, types ``A`` and ``B``.
Intersection types are a complementary concept to union types introduced
in PEP-484.

The primary use cases for intersection types include:

- mixin classes, which require certain APIs to be available;
- wrapper types, which add to the original type without monkey patching;
- combining multiple protocols into a single structural type;
- ad-hoc merging of TypedDict types; and

This PEP outlines the syntax, assignability, consistency rules, and
other aspects related to intersection types.

Introduction
============

PEP-484 introduced the concept of a union type, written ``Union[A, B]``.
as a type expression, it describes values of either type ``A`` or type ``B``.

For example,

::

    class A: ...
    class B: ...
    class C(A, B): ...
    class D(A): ...

    # PEP-604 was introduced to allow writing `Union[X, Y]` as `X | Y`
    def fu(value: A | B): ...

    fu(A())  # Valid
    fu(B())  # Valid
    fu(C())  # Valid
    fu(D())  # Valid

Intersection types provide a different (complementary) way of combining types.
The type expression ``A & B`` describes values which are consistent with both type ``A`` and type ``B``.

For example,

::

    def fi(value: A & B): ...

    fi(A())  # Invalid
    fi(B())  # Invalid
    fi(C())  # Valid
    fi(D())  # Invalid

here it is valid to call ``fi`` on an instance of ``C``, but invalid to call it with instances of
``A``, ``B`` or ``D``.

Motivation
==========

This allows

- the typing of class decorators which make predictable additions in capability
  to types. (ie. ``functools.total_ordering``)
- improved duck-typing (Mixing of protocols without redeclarations)
- improved typing of Mixins

Mixins
------

Mixin classes often have to assume a certain API, which is not implemented by the mixin, but needs
to be available in the class hierarchy where the mixin is used.
For example,

::

    class LoginRequiredMixin(AccessMixin):
        def dispatch(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                # calling a method of `AccessMixin`
        	    return self.handle_no_permission()  # Valid
            # calling a method of `View`
            return super().dispatch(request, *args, **kwargs)  # Invalid
            #              ^^^^^^^^ Cannot access member "dispatch" for type "AccessMixin"
            #                         Member "dispatch" is unknown

The ``LoginRequiredMixin`` is designed to be used with the ``View`` base class which defines the
``dispatch`` method.
Intersection types allow expressing that directly via

::

    from typing import Self

    class LoginRequiredMixin(AccessMixin):
        def dispatch(self: Self & View, request, *args, **kwargs):
            if not request.user.is_authenticated:
                # calling a method of `AccessMixin`
        	    return self.handle_no_permission()  # Valid
            # calling a method of `View`
            return super().dispatch(request, *args, **kwargs)  # Valid

    invalid = LoginRequiredMixin()  # error here
    # invalid now has an instance method where self is bound to a value
    # inconsistent with it's annotation.

Source: https://docs.djangoproject.com/en/3.2/topics/auth/default/#django.contrib.auth.mixins.LoginRequiredMixin


Specification
=============

This adds a type form to the ``typing`` module named ``Intersection``
and implements ``__and__`` for ``builtins.type``. ``Intersection`` is a type
form (todo defintion) that can be parametrized with with type expressions.

This exands the allowed use of ``typing.Self`` (hereafter ``Self``) for type
expressions that refer to the bound value of an instance method or classmethod
to include intersections that contain ``Self``. It is not valid to create an
instance of a type containing such an annotation without the other operands
of the intersection being consistent.
(see Mixins in motivations for a practical example)


Type system behavior
--------------------

(TODO: define or link to definitions of type expression and value expression)

``A & B`` is short-hand for ``Intersection[A, B]``. ``Intersection`` is still
needed when considering typevariable tuples.

An unparameterized ``Intersection`` as a type expression must be considered an
error by type checkers. It is possible to end up with an ``Intersection``
that has been parameterized but is empty. This can happen in the case of type
variable tuples. An empty intersection as a type expression is equilvant to
``typing.Never``.

An unparameterized ``Intersection`` as a value expression is not a type error,
but may not be possible to provide a meaningful type for at this time, see
below section on runtime typechecking support.

Given an ``Intersection[*Ts]`` as a type expression, a corresponding value
expression is considered to be consistent with it if and only if the value
expression would be consistent with all of the type expressions, ``*Ts``.

Given a value that has a type of ``Intersection[*Ts]``, use of the value is
consistent with the known type if at least one type in ``*Ts`` provides a
definition which is consistent, and that the use is consistent with the first
type in ``*Ts`` which provides a relevent defintion.

While this simplifies type checker behavior to allow cachable linear
short-circuiting complexity, the behavior here was not chosen for this reason,
see rationale section for more details.

Though it was not chosen for this quality, the potentially superlinear
complexity of some other potential semantics should be kept in mind by anyone
considering changing the semantics in the future as this may be a barrier
to usefulness of implementations.

Type-Checkers that are interested in providing tuning knobs for strictness
MAY provide additional confiurable warnings for certain patterns with
intersections that could cause ambiguity regarding gradual typing.. (see below)


Composability within the type system
------------------------------------

``Intersection`` does not forbid any incompatability of type parameters
(Neither statically or at runtime). It is unforseeable if other types or
special forms could be changed to be compatible with eachother in the future.

It is sufficient to detect the incompatability at time of assignment when a
value expression cannot be formed which is consistent with multiple
incompatablec type expressions, as the creation of a type to have an instance
of as a value should itself produce the appropriate error if impossible prior
to an attempt to create an instance to use for assignment.

``Intersection`` does not carry any inherent restrictions on where it can be
placed in a type expression.


Runtime specification behavior
------------------------------

At runtime, ``Intersection[*Ts]`` and ``TypeOne & TypeTwo`` each create an
object which can be introspected consistent with the methods provided for type
introspection in ``typing`` such as, but not limited to ``get_origin``


Runtime type checking considerations
------------------------------------

At this point in time, ``Intersection`` as a value expression is only
consistent with a type expression of ``object``, ``Any``, and a few internal
types that should not be publically used.

This is not a binding limitation on Intersection, and future PEPs which provide
ways to type methods which do runtime introspection should treat this the same
as other parameterizable type forms which exist to express typing concepts
and not to express a specific indivudal runtime type.


Optional checks which are not strictly about correctness
========================================================

Type checkers and/or linters may decide to provide opinionated rules.
A few anticipated ones are listed below.

Type checkers and linters MAY provide any of these or others but MUST NOT
use these rules to treat libraries which have not opted into these checks as
being in-error. The cases these detect have validity, but also have sharp edges
that some users may choose to want to avoid in their own code.


Allowing avoiding unintentional ambiguity with gradual types
------------------------------------------------------------

- Users may wish to ban ``Any`` or gradual types in intsersections.
- Users may wish to enforce that Gradual types are ordered after
  non-gradual types in intersections
- Detecting cases where non-disjoint use could introduce ordering concerns
  (See appendix below for one method of detecting potential ordering concerns)

Rationale
=========

Outside of the fact that we are specifying the intersections should be ordered
in python, very little about this should be surprising. The ordering allows
for allowing developer choice in resolving ambiguity, and comes with
a side-effect of allowing linear complexity when evaluating
intersections by type checkers

As ordering of an intersection has the potential to be controversial,
the below summarizes what was explored and the various tradeoffs

Ordering
--------

It was observed that by introducing an ordering on one direction of the
consistency checks, that for all of the anticipated cases involving fully typed
code, the desired behavior from the type system for motivating cases worked as
intended, and that for the case of ``Any & T``, it matched the behavior of
subclassing of ``Any``.

While the pure and unordered form would be identical for the vast majority of
cases we expect users of fully typed code to encounter, The combination of the
definition of  ``Any`` doubling for both compatability and uncertainty creates
a situation where it cannot be excluded from such an intersection, and that
none of the possible interpretations of it are likely to be satisfying for all
users.

There are a few potential unordered interpretations of ``Any & T``
(for this section, where T is a non-gradual type).
The one which was found to be most consistent with existing definitions in the
type system could not reduce this to either ``Any`` or ``T``, but would still,
to users of a type ``Any & T`` be identical to ``Any``. This would lead to a
significant increases in false negatives interacting with gradual typing.

Banning ``Any`` from intersections to prevent this edge case would create
significant complications for untyped imports, unbound type variables, and the
general purpose intent of ``Any`` as a means of compatability in the framework
of gradual typing.

Other considered ways of resolving this in particular was to reword ``Any``'s
compatability to be more flexible, and treat it as always yielding to a known
implementation; However, this would increase the complexity of ``Any``, as well
as create situations where diamond patterns *may* have been resolved, but the
type system would not know, leading to increased un-typable false-positives.

Choosing to err on the side of False positives would be better for those
wanting the immediate feedbacks on type safety in an IDE that many users have
attributed to productiveness.

Choosing to err on the side of false negatives would be more in line with the
definition of compatability provided by ``Any``

Since an unordered intersection can create an erosion of the barrier between
typed an untyped code, no longer coercing from one to another, but being
possible to mix and match, it is predictable that making a decision either way
on this would to lead to increased friction between typed and untyped code, and
increase pressure to more fully type code or to treat code that still can't be
expressed by the type, but which needed to interact with typed code as taboo.

The ordering allows expressing preferring either the False positives for the
implied possible diamond pattern with untyped things (``T & Any``) and a narrow
remedy for it (``P & T & Any``) where ``P`` is a protocol expressing how the
diamond pattern was actually resolved.

The ordering also allows expressing prefering not to get warnings for the
implied possible diamond pattern: (``Any & T``)

Neither of these provide warnings for things not provided by ``T``, the scope
of the ordering mattering is only in the overlap.

(TODO add table comparing effects of each option in each of meaningful cases, highlighting the equivalence to unordered in most cases)

Backwards Compatibility
=======================

This PEP expands the allowed use of ``Self`` to better handle mixins,
this change is not done in a backwards incompatible manner.

The implementation of ``__and__`` for the builtin ``type`` may result in
runtime uses of type introspection to misbehave for user defined types using
a metaclass which defines ``__and__`` for some purpose.

The considerations are similar to the prior implementing of ``|`` for types.


Security Implications
=====================

None


How to Teach This
=================

TODO, comparisons to sets with union, comparisons using builtins (any, all)


Reference Implementation
========================

TODO

Comparison to other languages
=============================

When comparing what other languages with intersections, most do not provide an
intersection type.

Two notable comparisons with languages that do reinforce the decision to
include ordering.

While Kotlin (unlike Java) allows multiple inheritence, it does not allow a
diamond pattern to exist, allowing only one base to implement a defintion for
a method or attribute of a type. Kotlin's intersections therefore do not have
to consider non-disjoint intersections.

TypeScript treats an intersection containing Any to be Any.
This makes sense given that TypeScript only has structural typing
but does not map well into python when considering nominal subtyping, and
``Any & T`` (Where ``T`` is a non-gradual type) as a return type.

Additionally, For the case of non-disjoint intersections TypeScript does not
synthesize a minimum bound, but instead picks an arbitrary winner with an
undocumented sort. This is not ideal for python, but when considering only
structural typing, and with the availability of TypeScript's ``Pick`` and
``Omit``, it appears to be a non-issue for type expressiveness in TypeScript.


Rejected Alternatives
=====================

Naming it ``OrderedIntersection`` and without ``&``
---------------------------------------------------

Using ``Intersection`` presents a blocker on future work if anyone wants to
revisit the issues with a pure intersection, but ``UnorderedIntersection``
is available if anyone solves the issues.

Using ``&`` may be a significantly stronger blocker on pure intersections

This was a direction given serious consideration, however the
ergonomic benefits of ``&`` are substantial, ``OrderedIntersection``
being as long and verbose as it is will impact readability of complex
type signatures.

Additionally, we believe it is unlikely that all of the issues presented for
an unordered form in the rationale section are solvable in any version of
python that remains gradually typed, has both structural and nominal subtyping,
and allows for resolvable diamond patterns without adversely affecting the
needs or ergonomics for some users.

Such a version of python would already likely require a python 4.0,
allowing revisiting of both the name and operator use.

Apendices
=========

A heuristic for non-disjoint use and ordering concerns
------------------------------------------------------

There is a way to determine where the ordering actually matters.

As stated above, The ordering mattering is valid, but some libraries may want
to flag it if it comes up in their own code to be sure they are aware of the
potential sharp edges.

A reductive summary of this is that the ordering matters when there is an
unresolved diamond pattern, and that gradual types in their infinite
compatability conversely provide infinitely many possible diamond patterns.

While type checkers and linters are free to implement their own heuristics
for this which behave differently to better match the actual use cases
their users have, one set of rules for determining this are as follows:

Given any number of types, if for any identifier defined on any of the types
there is more than 1 non-exactly equivlaent type specification for that
identifier amoung the types, the ordering matters.

Any type that is considered to be a gradual type only provides 1 definition
for the identifiers it provides, but that 1 definition is not considered to be
"exactly equvalent" to one provided by a non-gradual type for the purpose of
this heuristic.

For instance, a type which provides a property ``x`` that resolves to ``Any``
conflicts with ``Any`` for this check. x is a property returning Any, which is
more strict than the behavior of ``Any`` when considering substitutability

This means the inclusion of ``Any`` with a non-Any would be a reason to flag
under this rule.

However, ``Callable[..., Any]`` is also a gradual type.
``Callable[..., Any] & SupportsAbs`` does not have multiple definitions
for any identifier, as ``SupportsAbs`` does not provide ``__call__``
(or any of the other things provided by ``Callable``) in an incomaptible way.

Beyond this, we also have to look at the effects of introducing an unknown
or partially unknown type through type variables on ambiguity.

For function scoped type variables
(type checkers do not apply variance to these)

- If the type variable participates in an intersection in a type expression for
  a parameter of the function, the ordering has the potential to matter.

For class scoped type variables as well as intersections as type parameters
to generics and typing special forms (i.e. ``type[T & Protocol]``):

- covariant and invariant TypeVariables should only be included if a bound is
  provided, and the provided bound should be used for the check.

- contravariant TypeVariables should be checked using a bound if provided, or
  otherwise be treated as Any

Footnotes
=========

TODO


Copyright
=========

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.