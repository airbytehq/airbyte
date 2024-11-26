#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._cave._cavefast import NoneType
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignGeneric,
    HintSignNewType,
    HintSignTypeVar,
)
from beartype._data.hint.pep.sign.datapepsignset import HINT_SIGNS_UNION

# Intentionally import PEP 484-compliant "typing" type hint factories rather
# than possibly PEP 585-compliant "beartype.typing" type hint factories.
from typing import (
    Generic,
    Optional,
    Tuple,
)

# ....................{ HINTS                              }....................
HINT_PEP484_TUPLE_EMPTY = Tuple[()]
'''
:pep:`484`-compliant empty fixed-length tuple type hint.
'''

# ....................{ TESTERS ~ ignorable                }....................
def is_hint_pep484_ignorable_or_none(
    hint: object, hint_sign: HintSign) -> Optional[bool]:
    '''
    ``True`` only if the passed object is a :pep:`484`-compliant **ignorable
    type hint,** ``False`` only if this object is a :pep:`484`-compliant
    unignorable type hint, and ``None`` if this object is *not* `PEP
    484`_-compliant.

    Specifically, this tester function returns ``True`` only if this object is
    a deeply ignorable :pep:`484`-compliant type hint, including:

    * A parametrization of the :class:`typing.Generic` abstract base class (ABC)
      by one or more type variables. As the name implies, this ABC is generic
      and thus fails to impose any meaningful constraints. Since a type variable
      in and of itself also fails to impose any meaningful constraints, these
      parametrizations are safely ignorable in all possible contexts: e.g.,

      .. code-block:: python

         from typing import Generic, TypeVar
         T = TypeVar('T')
         def noop(param_hint_ignorable: Generic[T]) -> T: pass

    * The :func:`NewType` closure factory function passed an ignorable child
      type hint. Unlike most :mod:`typing` constructs, that function does *not*
      cache the objects it returns: e.g.,

      .. code-block:: python

         >>> from typing import NewType
         >>> NewType('TotallyNotAStr', str) is NewType('TotallyNotAStr', str)
         False

      Since this implies every call to ``NewType({same_name}, object)`` returns
      a new closure, the *only* means of ignoring ignorable new type aliases is
      dynamically within this function.
    * The :data:`Optional` or :data:`Union` singleton subscripted by one or
      more ignorable type hints (e.g., ``typing.Union[typing.Any, bool]``).
      Why? Because unions are by definition only as narrow as their widest
      child hint. However, shallowly ignorable type hints are ignorable
      precisely because they are the widest possible hints (e.g.,
      :class:`object`, :attr:`typing.Any`), which are so wide as to constrain
      nothing and convey no meaningful semantics. A union of one or more
      shallowly ignorable child hints is thus the widest possible union,
      which is so wide as to constrain nothing and convey no meaningful
      semantics. Since there exist a countably infinite number of possible
      :data:`Union` subscriptions by one or more ignorable type hints, these
      subscriptions *cannot* be explicitly listed in the
      :data:`HINTS_REPR_IGNORABLE_SHALLOW` frozenset. Instead, these
      subscriptions are dynamically detected by this tester at runtime and thus
      referred to as **deeply ignorable type hints.**

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as this tester is only safely callable
    by the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.
    hint_sign : HintSign
        **Sign** (i.e., arbitrary object uniquely identifying this hint).

    Returns
    ----------
    Optional[bool]
        Either:

        * If this object is :pep:`484`-compliant:

          * If this object is a ignorable, ``True``.
          * Else, ``False``.

        * If this object is *not* :pep:`484`-compliant, ``None``.
    '''
    # print(f'Testing PEP 484 hint {repr(hint)} [{repr(hint_sign)}] deep ignorability...')

    #FIXME: Remove this *AFTER* properly supporting type variables. For
    #now, ignoring type variables is required ta at least shallowly support
    #generics parametrized by one or more type variables.

    # For minor efficiency gains, the following tests are intentionally ordered
    # in descending likelihood of a match.
    #
    # If this hint is a PEP 484-compliant type variable, unconditionally return
    # true. Type variables require non-trivial and currently unimplemented
    # decorator support.
    if hint_sign is HintSignTypeVar:
        return True
    # Else, this hint is *NOT* a PEP 484-compliant type variable.
    #
    # If this hint is a PEP 484-compliant union...
    elif hint_sign in HINT_SIGNS_UNION:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.utilpepget import get_hint_pep_args
        from beartype._util.hint.utilhinttest import is_hint_ignorable

        # Return true only if one or more child hints of this union are
        # recursively ignorable. See the function docstring.
        return any(
            is_hint_ignorable(hint_child)
            for hint_child in get_hint_pep_args(hint)
        )
    # Else, this hint is *NOT* a PEP 484-compliant union.
    #
    # If this hint is a PEP 484-compliant generic...
    elif hint_sign is HintSignGeneric:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.utilpepget import (
            get_hint_pep_origin_or_none)

        # print(f'Testing generic hint {repr(hint)} deep ignorability...')
        # If this generic is the "typing.Generic" superclass directly
        # parametrized by one or more type variables (e.g.,
        # "typing.Generic[T]"), return true.
        #
        # Note that we intentionally avoid calling the
        # get_hint_pep_origin_type_isinstanceable_or_none() function here, which
        # has been intentionally designed to exclude PEP-compliant type hints
        # originating from "typing" type origins for stability reasons.
        if get_hint_pep_origin_or_none(hint) is Generic:
            # print(f'Testing generic hint {repr(hint)} deep ignorability... True')
            return True
        # Else, this generic is *NOT* the "typing.Generic" superclass directly
        # parametrized by one or more type variables and thus *NOT* an
        # ignorable non-protocol.
        #
        # Note that this condition being false is *NOT* sufficient to declare
        # this hint to be unignorable. Notably, the type origin originating
        # both ignorable and unignorable protocols is "Protocol" rather than
        # "Generic". Ergo, this generic could still be an ignorable protocol.
        # print(f'Testing generic hint {repr(hint)} deep ignorability... False')
    # Else, this hint is *NOT* a PEP 484-compliant generic.
    #
    # If this hint is a PEP 484-compliant new type...
    elif hint_sign is HintSignNewType:
        # Avoid circular import dependencies.
        from beartype._util.hint.utilhinttest import is_hint_ignorable
        from beartype._util.hint.pep.proposal.pep484.utilpep484newtype import (
            get_hint_pep484_newtype_alias)

        # Return true only if this hint aliases an ignorable child type hint.
        return is_hint_ignorable(get_hint_pep484_newtype_alias(hint))
    # Else, this hint is *NOT* a PEP 484-compliant new type.

    # Return "None", as this hint is unignorable only under PEP 484.
    return None

# ....................{ REDUCERS                           }....................
#FIXME: Replace the ambiguous parameter:
#* "hint: object" with the unambiguous parameter "hint: Literal[None]" *AFTER*
#  we drop support for Python 3.7. *sigh*

# Note that this reducer is intentionally typed as returning "type" rather than
# "NoneType". While the former would certainly be preferable, mypy erroneously
# emits false positives when this reducer is typed as returning "NoneType":
#     beartype/_util/hint/pep/proposal/pep484/utilpep484.py:190: error: Variable
#     "beartype._cave._cavefast.NoneType" is not valid as a type [valid-type]
def reduce_hint_pep484_none(hint: object, *args, **kwargs) -> type:
    '''
    Reduce the passed :pep:`484`-compliant :data:`None` type hint to the type of
    that type hint (i.e., the builtin :class:`types.NoneType` class).

    While *not* explicitly defined by the :mod:`typing` module, :pep:`484`
    explicitly supports this singleton:

        When used in a type hint, the expression :data:`None` is considered
        equivalent to ``type(None)``.

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Type variable to be reduced.

    All remaining passed arguments are silently ignored.

    Returns
    ----------
    NoneType
        Type of the :data:`None` singleton.
    '''
    assert hint is None, f'Type hint {hint} not "None" singleton.'

    # Unconditionally return the type of the "None" singleton.
    return NoneType
