#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **callable utilities** (i.e., callables
specifically applicable to :pep:`484`-compliant decorators used to decorate
user-defined callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from collections.abc import Callable

# ....................{ TESTERS                            }....................
def is_func_pep484_notypechecked(func: Callable) -> bool:
    '''
    ``True`` only if the passed callable was decorated by the
    :pep:`484`-compliant :func:`typing.no_type_check` decorator instructing
    both static and runtime type checkers to ignore that callable with respect
    to type-checking (and thus preserve that callable as is).

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    ----------
    bool
        ``True`` only if that callable was decorated by the
        :pep:`484`-compliant :func:`typing.no_type_check` decorator.
    '''

    # Return true only if that callable declares a dunder attribute hopefully
    # *ONLY* declared on that callable by the @typing.no_type_check decorator.
    return getattr(func, '__no_type_check__', False) is True
