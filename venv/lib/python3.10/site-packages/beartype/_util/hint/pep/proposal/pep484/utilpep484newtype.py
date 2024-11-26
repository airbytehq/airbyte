#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **new type hint utilities** (i.e.,
callables generically applicable to :pep:`484`-compliant types).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484Exception
from beartype.typing import Any
from beartype._data.hint.pep.sign.datapepsigns import HintSignNewType
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
from types import FunctionType

# ....................{ TESTERS                            }....................
# If the active Python interpreter targets Python >= 3.10 and thus defines
# "typing.NewType" type hints as instances of that class, implement this tester
# unique to prior Python versions to raise an exception.
if IS_PYTHON_AT_LEAST_3_10:
    def is_hint_pep484_newtype_pre_python310(hint: object) -> bool:
        raise BeartypeDecorHintPep484Exception(
            'is_hint_pep484_newtype_pre_python310() assumes Python < 3.10, '
            'but current Python interpreter targets Python >= 3.10.'
        )
# Else, the active Python interpreter targets Python < 3.10 and thus defines
# "typing.NewType" type hints as closures returned by that function. Since
# these closures are sufficiently dissimilar from all other type hints to
# require unique detection, implement this tester unique to this obsolete
# Python version to detect these closures.
else:
    def is_hint_pep484_newtype_pre_python310(hint: object) -> bool:

        # Return true only if...
        return (
            # This hint is a pure-Python function *AND*...
            #
            # Note that we intentionally do *NOT* call the callable() builtin
            # here, as that builtin erroneously returns false positives for
            # non-standard classes defining the __call__() dunder method to
            # unconditionally raise exceptions. Critically, this includes most
            # PEP 484-compliant type hints, which naturally fail to define both
            # the "__module__" *AND* "__qualname__" dunder instance variables
            # accessed below. Shoot me now, fam.
            isinstance(hint, FunctionType) and
            # This callable is a closure created and returned by the
            # typing.NewType() function. Note that:
            #
            # * The "__module__" and "__qualname__" dunder instance variables
            #   are *NOT* generally defined for arbitrary objects but are
            #   specifically defined for callables.
            # * "__qualname__" is safely available under Python >= 3.3.
            # * This test derives from the observation that the concatenation
            #   of this callable's "__qualname__" and "__module" dunder
            #   instance variables suffices to produce a string unambiguously
            #   identifying whether this hint is a "NewType"-generated closure:
            #       >>> from typing import NewType
            #       >>> UserId = t.NewType('UserId', int)
            #       >>> UserId.__qualname__
            #       >>> 'NewType.<locals>.new_type'
            #       >>> UserId.__module__
            #       >>> 'typing'
            f'{hint.__module__}.{hint.__qualname__}'.startswith(
                'typing.NewType.')
        )


is_hint_pep484_newtype_pre_python310.__doc__ = '''
    :data:`True` only if the passed object is a Python < 3.10-specific
    :pep:`484`-compliant **new type** (i.e., closure created and returned by
    the :func:`typing.NewType` closure factory function).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **New type aliases are a complete farce and thus best avoided.**
    Specifically, these PEP-compliant type hints are *not* actually types but
    rather **identity closures** that return their passed parameters as is.
    Instead, where distinct types are:

    * *Not* required, simply annotate parameters and return values with the
      desired superclasses.
    * Required, simply:

      * Subclass the desired superclasses as usual.
      * Annotate parameters and return values with those subclasses.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        :data:`True` only if this object is a Python < 3.10-specific
        :pep:`484`-compliant new type.
    '''

# ....................{ GETTERS                            }....................
def get_hint_pep484_newtype_alias(
    hint: Any, exception_prefix: str = '') -> object:
    '''
    **Non-new type type hint** (i.e., PEP-compliant type hint that is *not* a
    new type) encapsulated by the passed **new type** (i.e., object created and
    returned by the :pep:`484`-compliant :func:`typing.NewType` type hint
    factory).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    object
        Non-new type type hint encapsulated by this new type.

    Raises
    ----------
    BeartypeDecorHintPep484Exception
        If this object is *not* a new type.

    See Also
    ----------
    :func:`is_hint_pep484_newtype`
        Further commentary.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_sign,
        get_hint_pep_sign_or_none,
    )

    # If this object is *NOT* a new type, raise an exception.
    if get_hint_pep_sign(hint) is not HintSignNewType:
        raise BeartypeDecorHintPep484Exception(
            f'{exception_prefix}type hint {repr(hint)} not "typing.NewType".')
    # Else, this object is a new type.

    # While the Universe continues infinitely expanding...
    while True:
        # Reduce this new type to the type hint encapsulated by this new type,
        # which itself is possibly a nested new type. Oh, it happens.
        hint = hint.__supertype__

        # If this type hint is *NOT* a nested new type, break this iteration.
        if get_hint_pep_sign_or_none(hint) is not HintSignNewType:
            break
        # Else, this type hint is a nested new type. In this case, continue
        # iteratively unwrapping this nested new type.

    # Return this non-new type type hint.
    return hint

# ....................{ REDUCERS                           }....................
def reduce_hint_pep484_newtype(
    hint: object, exception_prefix: str, *args, **kwargs) -> object:
    '''
    Reduce the passed **new type** (i.e., object created and returned by the
    :pep:`484`-compliant :func:`typing.NewType` type hint factory) to the
    **non-new type type hint** (i.e., PEP-compliant type hint that is *not* a
    new type) encapsulated by this new type.

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This reducer has worst-case linear time complexity** :math:`O(k)` for
    :math:`k` the number of **nested new types** (e.g., :math:`k = 2` for the
    doubly nested new type ``NewType('a', NewType('b', int))``) embedded within
    this new type. Pragmatically, this reducer has average-case constant time
    complexity :math:`O(1)`. Why? Because nested new types are extremely rare.
    Almost all real-world new types are non-nested. Indeed, it took three years
    for a user to submit an issue presenting the existence of a nested new type.

    Parameters
    ----------
    hint : object
        Final type hint to be reduced.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message.

    All remaining passed arguments are silently ignored.

    Returns
    ----------
    type
        Non-new type type hint encapsulated by this new type.
    '''

    # Reduce this new type to the non-new type type hint encapsulated by this
    # new type.
    #
    # Note that this reducer *CANNOT* be reduced to an efficient alias of the
    # get_hint_pep484_newtype_alias() getter, as this reducer accepts ignorable
    # arguments *NOT* accepted by that getter.
    return get_hint_pep484_newtype_alias(
        hint=hint, exception_prefix=exception_prefix)
