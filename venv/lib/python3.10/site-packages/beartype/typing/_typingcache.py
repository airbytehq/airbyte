#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype typing callable caching** (i.e., general-purpose memoization of
function and method calls intended to be called *only* from submodules of this
subpackage) utilities.

This private submodule implements only a minimal subset of the caching
functionality implemented by the general-purpose
:mod:`beartype._util.cache.utilcachecall` submodule, from which this submodule
was originally derived. Since the latter transitively imports from the
:mod:`beartype.typing` subpackage at module scope, submodules of the
:mod:`beartype.typing` subpackage *cannot* safely import from the
:mod:`beartype._util.cache.utilcachecall` submodule at module scope. Ergo, the
existence of this submodule.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from functools import wraps

# Note that we intentionally:
# * Avoid importing these type hint factories from "beartype.typing", as that
#   would induce a circular import dependency. Instead, we manually import the
#   relevant type hint factories conditionally depending on the version of the
#   active Python interpreter. *sigh*
# * Test the negation of this condition first. Why? Because mypy quietly
#   defecates all over itself if the order of these two branches is reversed.
#   Yeah. It's as bad as it sounds.
if not IS_PYTHON_AT_LEAST_3_9:
    from typing import Callable, Dict  # type: ignore[misc]
# Else, the active Python interpreter targets Python >= 3.9 and thus supports
# PEP 585. In this case, embrace non-deprecated PEP 585-compliant type hints.
else:
    from collections.abc import Callable
    Dict = dict  # type: ignore[misc]

# ....................{ CONSTANTS                          }....................
_SENTINEL = object()
'''
Sentinel object of arbitrary value.
'''

# ....................{ DECORATORS                         }....................
def callable_cached_minimal(func: Callable) -> Callable:
    '''
    **Memoize** (i.e., efficiently cache and return all previously returned
    values of the passed callable as well as all previously raised exceptions
    of that callable previously rather than inefficiently recalling that
    callable) the passed callable.

    Parameters
    ----------
    func : Callable
        Callable to be memoized.

    Returns
    ----------
    Callable
        Closure wrapping this callable with memoization.

    See Also
    ----------
    :func:`beartype._util.cache.utilcachecall.callable_cached`
        Further details.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # Dictionary mapping a tuple of all flattened parameters passed to each
    # prior call of the decorated callable with the value returned by that
    # call if any (i.e., if that call did *NOT* raise an exception).
    params_flat_to_return_value: Dict[tuple, object] = {}

    # get() method of this dictionary, localized for efficiency.
    params_flat_to_return_value_get = params_flat_to_return_value.get

    # Dictionary mapping a tuple of all flattened parameters passed to each
    # prior call of the decorated callable with the exception raised by that
    # call if any (i.e., if that call raised an exception).
    params_flat_to_exception: Dict[tuple, Exception] = {}

    # get() method of this dictionary, localized for efficiency.
    params_flat_to_exception_get = params_flat_to_exception.get

    @wraps(func)
    def _callable_cached(*args):
        f'''
        Memoized variant of the {func.__name__}() callable.

        See Also
        ----------
        :func:`callable_cached`
            Further details.
        '''

        # If passed only one positional argument, minimize space consumption by
        # flattening this tuple of only that argument into that argument. Since
        # tuple items are necessarily hashable, this argument is necessarily
        # hashable as well and thus permissible as a dictionary key below.
        if len(args) == 1:
            params_flat = args[0]
        # Else, one or more positional arguments are passed. In this case,
        # reuse this tuple as is.
        else:
            params_flat = args

        # Attempt to...
        try:
            #FIXME: Optimize the params_flat_to_exception_get() case, please.
            #Since "None" is *NOT* a valid exception, we shouldn't need a
            #sentinel for safety here. Instead, this should suffice:
            #    exception = params_flat_to_exception_get(params_flat)

            #    # If this callable previously raised an exception when called with
            #    # these parameters, re-raise the same exception.
            #    if exception:
            #        raise exception

            # Exception raised by a prior call to the decorated callable when
            # passed these parameters *OR* the sentinel placeholder otherwise
            # (i.e., if this callable either has yet to be called with these
            # parameters *OR* has but failed to raise an exception).
            #
            # Note that this call raises a "TypeError" exception if any item of
            # this flattened tuple is unhashable.
            exception = params_flat_to_exception_get(params_flat, _SENTINEL)

            # If this callable previously raised an exception when called with
            # these parameters, re-raise the same exception.
            if exception is not _SENTINEL:
                raise exception  # pyright: ignore[reportGeneralTypeIssues]
            # Else, this callable either has yet to be called with these
            # parameters *OR* has but failed to raise an exception.

            # Value returned by a prior call to the decorated callable when
            # passed these parameters *OR* a sentinel placeholder otherwise
            # (i.e., if this callable has yet to be passed these parameters).
            return_value = params_flat_to_return_value_get(
                params_flat, _SENTINEL)

            # If this callable has already been called with these parameters,
            # return the value returned by that prior call.
            if return_value is not _SENTINEL:
                return return_value
            # Else, this callable has yet to be called with these parameters.

            # Attempt to...
            try:
                # Call this parameter with these parameters and cache the value
                # returned by this call to these parameters.
                return_value = params_flat_to_return_value[params_flat] = func(
                    *args)
            # If this call raises an exception...
            except Exception as exception:
                # Cache this exception to these parameters.
                params_flat_to_exception[params_flat] = exception

                # Re-raise this exception.
                raise exception
        # If one or more objects either passed to *OR* returned from this call
        # are unhashable, perform this call as is *WITHOUT* memoization. While
        # non-ideal, stability is better than raising a fatal exception.
        except TypeError:
            return func(*args)

        # Return this value.
        return return_value

    # Return this wrapper.
    return _callable_cached
