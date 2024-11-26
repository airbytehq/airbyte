#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **argument type hint
utilities** (i.e., callables generically applicable to child type hints
subscripting both :pep:`484`- and :pep:`585`-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep585Exception
from beartype.typing import Tuple

# ....................{ GETTERS                            }....................
def get_hint_pep484585_args_1(hint: object, exception_prefix: str) -> object:
    '''
    Argument subscripting the passed :pep:`484`- or :pep:`585`-compliant
    **single-argument type hint** (i.e., hint semantically subscriptable
    (indexable) by exactly one argument).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This higher-level getter should always be called in lieu of directly
    accessing the low-level** ``__args__`` **dunder attribute,** which is
    typically *not* validated at runtime and thus should *not* be assumed to be
    sane. Although the :mod:`typing` module usually validates the arguments
    subscripting :pep:`484`-compliant type hints and thus the ``__args__``
    **dunder attribute at hint instantiation time, C-based CPython internals
    fail to similarly validate the arguments subscripting :pep:`585`-compliant
    type hints at any time:

    .. code-block:: python

        >>> import typing
        >>> typing.Type[str, bool]
        TypeError: Too many parameters for typing.Type; actual 2, expected 1
        >>> type[str, bool]
        type[str, bool]   # <-- when everything is okay, nothing is okay

    Parameters
    ----------
    hint : Any
        PEP-compliant type hint to be inspected.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    ----------
    object
        Single argument subscripting this hint.

    Raises
    ----------
    BeartypeDecorHintPep585Exception
        If this hint is subscripted by either:

        * *No* arguments.
        * Two or more arguments.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args

    # Tuple of all arguments subscripting this hint.
    hint_args = get_hint_pep_args(hint)

    # If this hint is *NOT* subscripted by one argument, raise an exception.
    if len(hint_args) != 1:
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        raise BeartypeDecorHintPep585Exception(
            f'{exception_prefix}PEP 585 type hint {repr(hint)} '
            f'not subscripted (indexed) by one argument (i.e., '
            f'subscripted by {len(hint_args)} != 1 arguments).'
        )
    # Else, this hint is subscripted by one argument.

    # Return this argument as is.
    return hint_args[0]


def get_hint_pep484585_args_3(
    hint: object, exception_prefix: str) -> Tuple[object, object, object]:
    '''
    3-tuple of the three arguments subscripting the passed :pep:`484`- or
    :pep:`585`-compliant **three-argument type hint** (i.e., hint semantically
    subscriptable (indexable) by exactly three arguments).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Any
        PEP-compliant type hint to be inspected.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    ----------
    Tuple[object, object, object]
        3-tuple of the three arguments subscripting this hint.

    Raises
    ----------
    BeartypeDecorHintPep585Exception
        If this hint is subscripted by either:

        * *No* arguments.
        * One or two arguments.
        * Four or more arguments.

    See Also
    ----------
    :func:`get_hint_pep484585_args_1`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args

    # Tuple of all arguments subscripting this hint.
    hint_args = get_hint_pep_args(hint)

    # If this hint is *NOT* subscripted by three arguments, raise an exception.
    if len(hint_args) != 3:
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        raise BeartypeDecorHintPep585Exception(
            f'{exception_prefix}PEP 585 type hint {repr(hint)} '
            f'not subscripted (indexed) by three arguments (i.e., '
            f'subscripted by {len(hint_args)} != 3 arguments).'
        )
    # Else, this hint is subscripted by one argument.

    # Return this tuple of arguments as is.
    return hint_args  # type: ignore[return-value]
