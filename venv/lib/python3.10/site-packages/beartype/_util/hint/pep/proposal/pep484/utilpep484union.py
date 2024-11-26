#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **union type hint utilities** (i.e.,
callables generically applicable to :pep:`484`-compliant :attr:`typing.Union`
subscriptions).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Union

# ....................{ MAKERS                             }....................
def make_hint_pep484_union(hints: tuple) -> object:
    '''
    :pep:`484`-compliant **union type hint** (:attr:`typing.Union`
    subscription) synthesized from the passed tuple of two or more
    PEP-compliant type hints if this tuple contains two or more items, the one
    PEP-compliant type hint in this tuple if this tuple contains only one item,
    *or* raise an exception otherwise (i.e., if this tuple is empty).

    This maker is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the :attr:`typing.Union` type hint
    factory already caches its subscripted arguments.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.

    Returns
    ----------
    object
        Either:

        * If this tuple contains two or more items, the union type hint
          synthesized from these items.
        * If this tuple contains only one item, this item as is.

    Raises
    ----------
    :exc:`TypeError`
        If this tuple is empty.
    '''
    assert isinstance(hints, tuple), f'{repr(hints)} not tuple.'

    # These are the one-liners of our lives.
    return Union.__getitem__(hints)  # pyright: ignore[reportGeneralTypeIssues]
