#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **type variable utilities** (i.e.,
callables generically applicable to :pep:`484`-compliant type variables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484Exception
from beartype.typing import TypeVar
from beartype._util.cache.utilcachecall import callable_cached

# ....................{ GETTERS                            }....................
@callable_cached
def get_hint_pep484_typevar_bound_or_none(
    hint: TypeVar, exception_prefix: str = '') -> object:
    '''
    PEP-compliant type hint synthesized from all bounded constraints
    parametrizing the passed :pep:`484`-compliant **type variable** (i.e.,
    :class:`typing.TypeVar` instance) if any *or* :data:`None` otherwise (i.e.,
    if this type variable was parametrized by *no* bounded constraints).

    Specifically, if this type variable was parametrized by:

    #. One or more **constraints** (i.e., positional arguments passed by the
       caller to the :meth:`typing.TypeVar.__init__` call initializing this
       type variable), this getter returns a new **PEP-compliant union type
       hint** (i.e., :attr:`typing.Union` subscription) of those constraints.
    #. One **upper bound** (i.e., ``bound`` keyword argument passed by the
       caller to the :meth:`typing.TypeVar.__init__` call initializing this
       type variable), this getter returns that bound as is.
    #. Else, this getter returns the ``None`` singleton.

    Caveats
    ----------
    **This getter treats constraints and upper bounds as semantically
    equivalent,** preventing callers from distinguishing between these two
    technically distinct variants of type variable metadata.

    For runtime type-checking purposes, type variable constraints and bounds
    are sufficiently similar as to be semantically equivalent for all intents
    and purposes. To simplify handling of type variables, this getter
    ambiguously aggregates both into the same tuple.

    For static type-checking purposes, type variable constraints and bounds
    are *still* sufficiently similar as to be semantically equivalent for all
    intents and purposes. Any theoretical distinction between the two is likely
    to be lost on *most* engineers, who tend to treat the two interchangeably.
    To quote :pep:`484`:

        ...type constraints cause the inferred type to be _exactly_ one of the
        constraint types, while an upper bound just requires that the actual
        type is a subtype of the boundary type.

    Inferred types are largely only applicable to static type-checkers, which
    internally assign type variables contextual types inferred from set and
    graph theoretic operations on the network of all objects (nodes) and
    callables (edges) relating those objects. Runtime type-checkers have *no*
    analogous operations, due to runtime space and time constraints.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). If this type variable was parametrized
    by one or more constraints, the :attr:`typing.Union` type hint factory
    already caches these constraints; else, this getter performs no work. In
    any case, this getter effectively performs to work.

    Parameters
    ----------
    hint : object
        :pep:`484`-compliant type variable to be inspected.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    object
        Either:

        * If this type variable was parametrized by one or more constraints, a
          new PEP-compliant union type hint aggregating those constraints.
        * If this type variable was parametrized by an upper bound, that bound.
        * Else, :data:`None`.

    Raises
    ----------
    BeartypeDecorHintPep484Exception
        if this object is *not* a :pep:`484`-compliant type variable.
    '''

    # If this hint is *NOT* a type variable, raise an exception.
    if not isinstance(hint, TypeVar):
        raise BeartypeDecorHintPep484Exception(
            f'{exception_prefix}type hint {repr(hint)} '
            f'not PEP 484 type variable.'
        )
    # Else, this hint is a type variable.

    # If this type variable was parametrized by one or more constraints...
    if hint.__constraints__:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.proposal.pep484.utilpep484union import (
            make_hint_pep484_union)

        # Create and return the PEP 484-compliant union of these constraints.
        return make_hint_pep484_union(hint.__constraints__)
    # Else, this type variable was parametrized by *NO* constraints.
    #
    # If this type variable was parametrized by an upper bound, return that
    # bound as is.
    elif hint.__bound__ is not None:
        return hint.__bound__
    # Else, this type variable was parametrized by neither constraints *NOR* an
    # upper bound.

    # Return "None".
    return None

# ....................{ REDUCERS                           }....................
#FIXME: Remove this function *AFTER* deeply type-checking type variables.
def reduce_hint_pep484_typevar(
    hint: TypeVar, exception_prefix: str, *args, **kwargs) -> object:
    '''
    Reduce the passed :pep:`484`-compliant **type variable** (i.e.,
    :class:`typing.TypedDict` instance) to a lower-level type hint currently
    supported by :mod:`beartype`.

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Type variable to be reduced.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    All remaining passed arguments are silently ignored.

    Returns
    ----------
    object
        Lower-level type hint currently supported by :mod:`beartype`.
    '''

    # PEP-compliant type hint synthesized from all bounded constraints
    # parametrizing this type variable if any *OR* "None" otherwise.
    #
    # Note that this function call is intentionally passed positional rather
    # positional keywords for efficiency with respect to @callable_cached.
    hint_bound = get_hint_pep484_typevar_bound_or_none(hint, exception_prefix)
    # print(f'Reducing PEP 484 type variable {repr(hint)} to {repr(hint_bound)}...')
    # print(f'Reducing non-beartype PEP 593 type hint {repr(hint)}...')

    # Return either...
    return (
        # If this type variable was parametrized by *NO* bounded constraints,
        # this type variable preserved as is;
        hint
        if hint_bound is None else
        # Else, this type variable was parametrized by one or more bounded
        # constraints. In this case, these constraints.
        hint_bound
    )
