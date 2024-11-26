#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint getter utilities** (i.e., callables
validating querying type hints supported by :mod:`beartype`, regardless of
whether those hints comply with PEP standards or not).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.hint.pep.datapeprepr import HINTS_REPR_IGNORABLE_SHALLOW
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.nonpep.utilnonpeptest import (
    die_unless_hint_nonpep,
    is_hint_nonpep,
)
from beartype._util.hint.pep.utilpeptest import (
    die_if_hint_pep_unsupported,
    is_hint_pep,
    is_hint_pep_supported,
)

# ....................{ TESTERS                            }....................
#FIXME: Call this getter everywhere we currently call "repr(hint*)", please.
@callable_cached
def get_hint_repr(hint: object) -> str:
    '''
    **Representation** (i.e., machine-readable string returned by the
    :func:`repr` builtin when passed this hint) of this PEP-agnostic type hint.

    This getter is memoized for efficiency. Indeed, since the implementation of
    this getter trivially reduces to just ``repr(hint)``, memoization is the
    entire reason for the existence of this getter.

    Motivation
    ----------
    **This getter should always be called to efficiently obtain the
    representation of any type hint.** The comparatively less efficient
    :func:`repr` builtin should *never* be called to do so.

    Parameters
    ----------
    hint : object
        Type hint to be represented.

    Returns
    ----------
    str
        Representation of this hint.
    '''

    # Return the machine-readable representation of this hint.
    return repr(hint)
