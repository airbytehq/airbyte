#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`591`-compliant **type hint** (i.e., objects created by
subscripting the :obj:`typing.Final` type hint factory) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep591Exception
# from beartype._util.py.utilpyversion import IS_PYTHON_3_8

# ....................{ REDUCERS                           }....................
#FIXME: Remove *AFTER* deeply type-checking "Final[...]" type hints. For now,
#shallowly type-checking such hints by reduction to their subscripted arguments
#remains the sanest temporary work-around.
def reduce_hint_pep591(
    hint: object, exception_prefix: str, *args, **kwargs) -> object:
    '''
    Reduce the passed :pep:`591`-compliant **final type hint** (i.e.,
    subscription of the :obj:`typing.Final` type hint factory) to a lower-level
    type hint currently supported by :mod:`beartype`.

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Final type hint to be reduced.
    exception_prefix : str, optional
        Human-readable substring prefixing exception messages raised by this
        function.

    All remaining passed arguments are silently ignored.

    Returns
    ----------
    object
        Lower-level type hint currently supported by :mod:`beartype`.

    Raises
    ----------
    BeartypeDecorHintPep591Exception
        If this hint is subscripted by two or more child type hints.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args

    # Tuple of zero or more child type hints subscripting this type hint.
    hint_args = get_hint_pep_args(hint)

    # Number of child type hints subscripting this type hint.
    hint_args_len = len(hint_args)

    # If this hint is unsubscripted, reduce this hint to the ignorable type hint
    # "object".
    #
    # Note that PEP 591 bizarrely permits the "typing.Final" type hint factory
    # to remain unsubscripted:
    #     * With no type annotation. Example:
    #           ID: Final = 1
    #       The typechecker should apply its usual type inference mechanisms to
    #       determine the type of ID (here, likely, int). Note that unlike for
    #       generic classes this is not the same as Final[Any].
    #
    # Since runtime type-checkers *NEVER* infer types, this permissiveness
    # substantially reduces the usability of this edge case at runtime.
    # Nevertheless, this is a valid edge case. Technically, we could emit a
    # non-fatal warning to recommend the user explicitly type each unsubscripted
    # "typing.Final" type hint. Pragmatically, doing so would only harass large
    # codebases attempting to migrate to @beartype. Doing nothing is preferable.
    if hint_args_len == 0:
        hint = object
    # If, this hint is subscripted by exactly one child type hint, reduce this
    # hint to that child hint.
    elif hint_args_len == 1:
        hint = hint_args[0]
    # Else, this hint is subscripted by two or more child type hints. In this
    # case, raise an exception.
    #
    # Note that "typing.Final" already prohibits subscription by two or more
    # arguments. Ergo, this should *NEVER* happen: e.g.,
    #     >>> import typing
    #     >>> typing.Final[int, float]
    #     TypeError: typing.Final accepts only single type. Got (<class 'int'>,
    #     <class 'float'>).
    else:
        raise BeartypeDecorHintPep591Exception(
            f'{exception_prefix}PEP 591 type hint {repr(hint)} '
            f'erroneously subscripted by {hint_args_len} child type hints.'
        )

    # Return this reduced hint.
    return hint
