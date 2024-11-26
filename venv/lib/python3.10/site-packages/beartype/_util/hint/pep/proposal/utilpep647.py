#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`647`-compliant **type hint** (i.e., objects created by
subscripting the :obj:`typing.Final` type hint factory) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep647Exception
from beartype.typing import (
    Optional,
    Type,
)
from beartype._data.func.datafuncarg import ARG_NAME_RETURN

# ....................{ REDUCERS                           }....................
#FIXME: Unit test us up, please.
def reduce_hint_pep647(
    hint: object,
    arg_name: Optional[str],
    exception_prefix: str,
    *args, **kwargs
) -> Type[bool]:
    '''
    Reduce the passed :pep:`647`-compliant **type guard** (i.e.,
    subscription of the :obj:`typing.TypeGuard` type hint factory) to the
    builtin :class:`bool` class as advised by :pep:`647` when performing
    runtime type-checking if this hint annotates the return of some callable
    (i.e., if ``arg_name`` is ``"return"``) *or* raise an exception otherwise
    (i.e., if this hint annotates the return of *no* callable).

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Final type hint to be reduced.
    arg_name : Optional[str]
        Either:

        * If this hint annotates a parameter of some callable, the name of that
          parameter.
        * If this hint annotates the return of some callable, ``"return"``.
        * Else, :data:`None`.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    All remaining passed arguments are silently ignored.

    Returns
    ----------
    Type[bool]
        Builtin :class:`bool` class.

    Raises
    ----------
    BeartypeDecorHintPep647Exception
        If this type guard does *not* annotate the return of some callable
        (i.e., if ``arg_kind`` is *not* :data:`True`).
    '''

    # If this type guard annotates the return of some callable, reduce this type
    # guard to the builtin "bool" class. Sadly, type guards are useless at
    # runtime and exist exclusively as a means of superficially improving the
    # computational intelligence of (...wait for it) static type-checkers.
    if arg_name == ARG_NAME_RETURN:
        return bool
    # Else, this type guard does *NOT* annotate the return of some callable.

    # Raise an exception. Type guards are contextually valid *ONLY* as top-level
    # return annotations.
    raise BeartypeDecorHintPep647Exception(
        f'{exception_prefix}PEP 647 type hint "{repr(hint)}" '
        f'invalid in this type hint context (i.e., '
        f'"{repr(hint)}" valid only as non-nested return annotation).'
    )
