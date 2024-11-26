#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :mod:`functools` **globals** (i.e., global constants describing
the standard :mod:`functools` module bundled with CPython's standard library).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from functools import lru_cache

# ....................{ STRINGS                            }....................
@lru_cache
def _lru_cache_func(n: int) -> int:
    '''
    Arbitrary :func:`functools.lru_cache`-memoized function defined solely to
    inspect various dunder attributes common to all such functions.
    '''

    return n + 1


LRU_CACHE_TYPE = type(_lru_cache_func)
'''
C-based type of all low-level private objects created and returned by the
:func:`functools.lru_cache` decorator (e.g.,
:class:`functools._lru_cache_wrapper`).

This type enables functionality elsewhere to reliably detect when a function has
been decorated by that decorator. 
'''
# print(f'LRU_CACHE_TYPE: {LRU_CACHE_TYPE}')


# Delete this placeholder function now that we no longer require it as a
# negligible safety (and possible space complexity) measure.
del _lru_cache_func
