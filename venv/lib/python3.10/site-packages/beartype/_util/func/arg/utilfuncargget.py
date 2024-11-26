#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable parameter getter utilities** (i.e., callables
introspectively querying metadata on parameters accepted by arbitrary
callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype.typing import Optional
from beartype._data.hint.datahinttyping import (
    Codeobjable,
    TypeException,
)
from beartype._util.func.arg.utilfuncargiter import (
    ARG_META_INDEX_NAME,
    iter_func_args,
)
from beartype._util.func.utilfunccodeobj import get_func_codeobj
from collections.abc import Callable

# ....................{ GETTERS ~ arg                      }....................
#FIXME: Unit test us up, please.
def get_func_arg_first_name_or_none(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    is_unwrap: bool = True,
    exception_cls: TypeException = _BeartypeUtilCallableException,
) -> Optional[str]:
    '''
    Name of the first parameter listed in the signature of the passed
    pure-Python callable if any *or* :data:`None` otherwise (i.e., if that
    callable accepts *no* parameters and is thus parameter-less).

    Parameters
    ----------
    func : Codeobjable
        Pure-Python callable, frame, or code object to be inspected.
    is_unwrap: bool, optional
        :data:`True` only if this getter implicitly calls the
        :func:`.unwrap_func_all_closures_isomorphic` function. Defaults to :data:`True` for safety. See
        :func:`.iter_func_args` for further commentary.
    exception_cls : type, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallableException`.

    Returns
    ----------
    Optional[str]
        Either:

        * If that callable accepts one or more parameters, the name of the first
          parameter listed in the signature of that callable.
        * Else, :data:`None`.

    Raises
    ----------
    :exc:`exception_cls`
         If that callable is *not* pure-Python.
    '''

    # For metadata describing each parameter accepted by this callable...
    for arg_meta in iter_func_args(
        func=func,
        is_unwrap=is_unwrap,
        exception_cls=exception_cls,
    ):
        # Return the name of this parameter.
        return arg_meta[ARG_META_INDEX_NAME]  # type: ignore[return-value]
    # Else, the above "return" statement was *NOT* performed. In this case, this
    # callable accepts *NO* parameters.

    # Return "None".
    return None

# ....................{ GETTERS ~ args                     }....................
def get_func_args_flexible_len(
    # Mandatory parameters.
    func: Codeobjable,

    # Optional parameters.
    is_unwrap: bool = True,
    exception_cls: TypeException = _BeartypeUtilCallableException,
) -> int:
    '''
    Number of **flexible parameters** (i.e., parameters passable as either
    positional or keyword arguments but *not* positional-only, keyword-only,
    variadic, or other more constrained kinds of parameters) accepted by the
    passed pure-Python callable.

    Parameters
    ----------
    func : Codeobjable
        Pure-Python callable, frame, or code object to be inspected.
    is_unwrap: bool, optional
        :data:`True` only if this getter implicitly calls the
        :func:`.unwrap_func_all_closures_isomorphic` function. Defaults to :data:`True` for safety. See
        :func:`.iter_func_args` for further commentary.
    exception_cls : type, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallableException`.

    Returns
    ----------
    int
        Number of flexible parameters accepted by this callable.

    Raises
    ----------
    :exc:`exception_cls`
         If that callable is *not* pure-Python.
    '''

    # Code object underlying the passed pure-Python callable unwrapped.
    func_codeobj = get_func_codeobj(
        func=func,
        is_unwrap=is_unwrap,
        exception_cls=exception_cls,
    )

    # Return the number of flexible parameters accepted by this callable.
    return func_codeobj.co_argcount


#FIXME: Unit test us up, please.
def get_func_args_nonvariadic_len(
    # Mandatory parameters.
    func: Codeobjable,

    # Optional parameters.
    is_unwrap: bool = True,
    exception_cls: TypeException = _BeartypeUtilCallableException,
) -> int:
    '''
    Number of **non-variadic parameters** (i.e., parameters passable as either
    positional, positional-only, keyword, or keyword-only arguments) accepted by
    the passed pure-Python callable.

    Parameters
    ----------
    func : Codeobjable
        Pure-Python callable, frame, or code object to be inspected.
    is_unwrap: bool, optional
        :data:`True` only if this getter implicitly calls the
        :func:`.unwrap_func_all_closures_isomorphic` function. Defaults to :data:`True` for safety. See
        :func:`.iter_func_args` for further commentary.
    exception_cls : type, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallableException`.

    Returns
    ----------
    int
        Number of flexible parameters accepted by this callable.

    Raises
    ----------
    :exc:`exception_cls`
         If that callable is *not* pure-Python.
    '''

    # Code object underlying the passed pure-Python callable unwrapped.
    func_codeobj = get_func_codeobj(
        func=func,
        is_unwrap=is_unwrap,
        exception_cls=exception_cls,
    )

    # Return the number of non-variadic parameters accepted by this callable.
    return func_codeobj.co_argcount + func_codeobj.co_kwonlyargcount
