#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable wrapper** (i.e., higher-level callable, typically
implemented as a decorator, wrapping a lower-level callable) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableWrapperException
from beartype.typing import Any
from collections.abc import Callable

# ....................{ UNWRAPPERS                         }....................
#FIXME: Unit test us up, please.
def unwrap_func_once(func: Any) -> Callable:
    '''
    Immediate **wrappee** (i.e., callable wrapped by the passed wrapper
    callable) of the passed higher-level **wrapper** (i.e., callable wrapping
    the wrappee callable to be returned) if the passed callable is a wrapper
    *or* that callable as is otherwise (i.e., if that callable is *not* a
    wrapper).

    Specifically, this getter undoes the work performed by:

    * A single use of the :func:`functools.wrap` decorator on the wrappee
      callable to be returned.
    * A single call to the :func:`functools.update_wrapper` function on the
      wrappee callable to be returned.

    Parameters
    ----------
    func : Callable
        Wrapper callable to be unwrapped.

    Returns
    ----------
    Callable
        The immediate wrappee callable wrapped by the passed wrapper callable.

    Raises
    ----------
    _BeartypeUtilCallableWrapperException
        If the passed callable is *not* a wrapper.
    '''

    # Immediate wrappee callable wrapped by the passed wrapper callable if any
    # *OR* "None" otherwise (i.e., if that callable is *NOT* a wrapper).
    func_wrappee = getattr(func, '__wrapped__', None)

    # If that callable is *NOT* a wrapper, raise an exception.
    if func_wrappee is None:
        raise _BeartypeUtilCallableWrapperException(
            f'Callable {repr(func)} not wrapper '
            f'(i.e., has no "__wrapped__" dunder attribute '
            f'defined by @functools.wrap or functools.update_wrapper()).'
        )
    # Else, that callable is a wrapper.

    # Return this immediate wrappee callable.
    return func_wrappee

# ....................{ UNWRAPPERS ~ all                   }....................
def unwrap_func_all(func: Any) -> Callable:
    '''
    Lowest-level **wrappee** (i.e., callable wrapped by the passed wrapper
    callable) of the passed higher-level **wrapper** (i.e., callable wrapping
    the wrappee callable to be returned) if the passed callable is a wrapper
    *or* that callable as is otherwise (i.e., if that callable is *not* a
    wrapper).

    Specifically, this getter iteratively undoes the work performed by:

    * One or more consecutive uses of the :func:`functools.wrap` decorator on
      the wrappee callable to be returned.
    * One or more consecutive calls to the :func:`functools.update_wrapper`
      function on the wrappee callable to be returned.

    Parameters
    ----------
    func : Callable
        Wrapper callable to be unwrapped.

    Returns
    ----------
    Callable
        Either:

        * If the passed callable is a wrapper, the lowest-level wrappee
          callable wrapped by that wrapper.
        * Else, the passed callable as is.
    '''

    #FIXME: Not even this suffices to avoid a circular import, sadly. *sigh*
    # Avoid circular import dependencies.
    # from beartype._util.func.utilfunctest import is_func_wrapper

    # While this callable still wraps another callable, unwrap one layer of
    # wrapping by reducing this wrapper to its next wrappee.
    while hasattr(func, '__wrapped__'):
    # while is_func_wrapper(func):
        func = func.__wrapped__  # type: ignore[attr-defined]

    # Return this wrappee, which is now guaranteed to *NOT* be a wrapper.
    return func


#FIXME: Unit test us up, please.
def unwrap_func_all_closures_isomorphic(func: Any) -> Callable:
    '''
    Lowest-level **non-isomorphic wrappee** (i.e., callable wrapped by the
    passed wrapper callable) of the passed higher-level **isomorphic wrapper**
    (i.e., closure wrapping the wrappee callable to be returned by accepting
    both a variadic positional and keyword argument and thus preserving both the
    positions and types of all parameters originally passed to that wrappee) if
    the passed callable is an isomorphic wrapper *or* that callable as is
    otherwise (i.e., if that callable is *not* an isomorphic wrapper).

    Specifically, this getter iteratively undoes the work performed by:

    * One or more consecutive decorations of the :func:`functools.wrap`
      decorator on the wrappee callable to be returned.
    * One or more consecutive calls to the :func:`functools.update_wrapper`
      function on the wrappee callable to be returned.

    Parameters
    ----------
    func : Callable
        Wrapper callable to be unwrapped.

    Returns
    ----------
    Callable
        Either:

        * If the passed callable is an isomorphic wrapper, the lowest-level
          non-isomorphic wrappee callable wrapped by that wrapper.
        * Else, the passed callable as is.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunctest import (
        is_func_closure_isomorphic,
        is_func_wrapper,
    )

    # While ...
    while (
        # That callable wraps a lower-level callable...
        is_func_wrapper(func) and
        # ...with a higher-level isomorphic wrapper...
        is_func_closure_isomorphic(func)
    ):
        # Undo one layer of wrapping by reducing the former to the latter.
        # print(f'Unwrapping isomorphic closure wrapper {func} to wrappee {func.__wrapped__}...')
        func = func.__wrapped__  # type: ignore[attr-defined]

    # Return this wrappee, which is now guaranteed to *NOT* be an isomorphic
    # wrapper but might very well still be a wrapper, which is fine.
    return func
