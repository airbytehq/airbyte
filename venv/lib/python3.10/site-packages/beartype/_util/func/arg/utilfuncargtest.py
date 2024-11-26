#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable parameter tester utilities** (i.e., callables
introspectively validating and testing parameters accepted by arbitrary
callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype._util.func.arg.utilfuncargiter import (
    ARG_META_INDEX_NAME,
    iter_func_args,
)
from beartype._util.func.utilfunccodeobj import get_func_codeobj
from beartype._data.hint.datahinttyping import (
    Codeobjable,
    TypeException,
)
from collections.abc import Callable
from inspect import (
    CO_VARARGS,
    CO_VARKEYWORDS,
)

# ....................{ VALIDATORS                         }....................
def die_unless_func_args_len_flexible_equal(
    # Mandatory parameters.
    func: Codeobjable,
    func_args_len_flexible: int,

    # Optional parameters.
    is_unwrap: bool = True,
    exception_cls: TypeException = _BeartypeUtilCallableException,
) -> None:
    '''
    Raise an exception unless the passed pure-Python callable accepts the
    passed number of **flexible parameters** (i.e., parameters passable as
    either positional or keyword arguments).

    Parameters
    ----------
    func : Codeobjable
        Pure-Python callable, frame, or code object to be inspected.
    func_args_len_flexible : int
        Number of flexible parameters to validate this callable as accepting.
    is_unwrap: bool, optional
        ``True`` only if this validator implicitly calls the
        :func:`unwrap_func_all_closures_isomorphic` function to unwrap this possibly higher-level
        wrapper into its possibly lowest-level wrappee *before* returning the
        code object of that wrappee. Note that doing so incurs worst-case time
        complexity ``O(n)`` for ``n`` the number of lower-level wrappees
        wrapped by this wrapper. Defaults to ``True`` for robustness. Why?
        Because this validator *must* always introspect lowest-level wrappees
        rather than higher-level wrappers. The latter typically do *not*
        accurately replicate the signatures of the former. In particular,
        decorator wrappers typically wrap decorated callables with variadic
        positional and keyword parameters (e.g., ``def _decorator_wrapper(*args,
        **kwargs)``). Since neither constitutes a flexible parameter, this
        validator raises an exception when passed such a wrapper with this
        boolean set to ``False``. For this reason, only set this boolean to
        ``False`` if you pretend to know what you're doing.
    exception_cls : type, optional
        Type of exception to be raised if this callable is neither a
        pure-Python function nor method. Defaults to
        :class:`_BeartypeUtilCallableException`.

    Raises
    ----------
    :exc:`exception_cls`
        If this callable either:

        * Is *not* callable.
        * Is callable but is *not* pure-Python.
        * Is a pure-Python callable accepting either more or less than this
          Number of flexible parameters.
    '''
    assert isinstance(func_args_len_flexible, int)

    # Avoid circular import dependencies.
    from beartype._util.func.arg.utilfuncargget import (
        get_func_args_flexible_len)

    # Number of flexible parameters accepted by this callable.
    func_args_len_flexible_actual = get_func_args_flexible_len(
        func=func,
        is_unwrap=is_unwrap,
        exception_cls=exception_cls,
    )

    # If this callable accepts more or less than this number of flexible
    # parameters, raise an exception.
    if func_args_len_flexible_actual != func_args_len_flexible:
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        raise exception_cls(
            f'Callable {repr(func)} flexible argument count '
            f'{func_args_len_flexible_actual} != {func_args_len_flexible}.'
        )
    # Else, this callable accepts exactly this number of flexible parameters.


#FIXME: Uncomment as needed.
# def die_unless_func_argless(
#     # Mandatory parameters.
#     func: Codeobjable,
#
#     # Optional parameters.
#     func_label: str = 'Callable',
#     exception_cls: Type[Exception] = _BeartypeUtilCallableException,
# ) -> None:
#     '''
#     Raise an exception unless the passed pure-Python callable is
#     **argumentless** (i.e., accepts *no* arguments).
#
#     Parameters
#     ----------
#     func : Codeobjable
#         Pure-Python callable, frame, or code object to be inspected.
#     func_label : str, optional
#         Human-readable label describing this callable in exception messages
#         raised by this validator. Defaults to ``'Callable'``.
#     exception_cls : type, optional
#         Type of exception to be raised if this callable is neither a
#         pure-Python function nor method. Defaults to
#         :class:`_BeartypeUtilCallableException`.
#
#     Raises
#     ----------
#     exception_cls
#         If this callable either:
#
#         * Is *not* callable.
#         * Is callable but is *not* pure-Python.
#         * Is a pure-Python callable accepting one or more parameters.
#     '''
#
#     # If this callable accepts one or more arguments, raise an exception.
#     if is_func_argless(
#         func=func, func_label=func_label, exception_cls=exception_cls):
#         assert isinstance(func_label, str), f'{repr(func_label)} not string.'
#         assert isinstance(exception_cls, type), (
#             f'{repr(exception_cls)} not class.')
#
#         raise exception_cls(
#             f'{func_label} {repr(func)} not argumentless '
#             f'(i.e., accepts one or more arguments).'
#         )

# ....................{ TESTERS ~ kind                     }....................
def is_func_argless(
    # Mandatory parameters.
    func: Codeobjable,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
) -> bool:
    '''
    :data:`True` only if the passed pure-Python callable is **argumentless**
    (i.e., accepts *no* arguments).

    Parameters
    ----------
    func : Codeobjable
        Pure-Python callable, frame, or code object to be inspected.
    exception_cls : type, optional
        Type of exception to be raised in the event of fatal error. Defaults to
        :class:`_BeartypeUtilCallableException`.

    Returns
    ----------
    bool
        :data:`True` only if the passed callable accepts *no* arguments.

    Raises
    ----------
    :exc:`exception_cls`
         If the passed callable is *not* pure-Python.
    '''

    # Code object underlying the passed pure-Python callable unwrapped.
    func_codeobj = get_func_codeobj(
        func=func, is_unwrap=False, exception_cls=exception_cls)

    # Return true only if this callable accepts neither...
    return not (
        # One or more non-variadic arguments *NOR*...
        is_func_arg_nonvariadic(func_codeobj) or
        # One or more variadic arguments.
        is_func_arg_variadic(func_codeobj)
    )

# ....................{ TESTERS ~ kind : non-variadic      }....................
#FIXME: Unit test us up, please.
def is_func_arg_nonvariadic(func: Codeobjable) -> bool:
    '''
    :data:`True` only if the passed pure-Python callable accepts any
    **non-variadic parameters** (i.e., one or more positional, positional-only,
    keyword, or keyword-only arguments).

    Parameters
    ----------
    func : Union[Callable, CodeType, FrameType]
        Pure-Python callable, frame, or code object to be inspected.

    Returns
    ----------
    bool
        :data:`True` only if that callable accepts any non-variadic parameters.

    Raises
    ----------
    _BeartypeUtilCallableException
         If that callable is *not* pure-Python.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.arg.utilfuncargget import (
        get_func_args_nonvariadic_len)

    # Return true only if this callable accepts any non-variadic parameters.
    return bool(get_func_args_nonvariadic_len(func))

# ....................{ TESTERS ~ kind : variadic          }....................
def is_func_arg_variadic(func: Codeobjable) -> bool:
    '''
    :data:`True` only if the passed pure-Python callable accepts any **variadic
    parameters** (i.e., either a variadic positional argument (e.g.,
    ``*args``) *or* a variadic keyword argument (e.g., ``**kwargs``)).

    Parameters
    ----------
    func : Union[Callable, CodeType, FrameType]
        Pure-Python callable, frame, or code object to be inspected.

    Returns
    ----------
    bool
        :data:`True` only if that callable accepts either:

        * Variadic positional arguments (e.g., ``*args``).
        * Variadic keyword arguments (e.g., ``**kwargs``).

    Raises
    ----------
    _BeartypeUtilCallableException
         If that callable is *not* pure-Python.
    '''

    # Return true only if this callable declares either...
    #
    # We can't believe it's this simple, either. But it is.
    return (
        # Variadic positional arguments *OR*...
        is_func_arg_variadic_positional(func) or
        # Variadic keyword arguments.
        is_func_arg_variadic_keyword(func)
    )


def is_func_arg_variadic_positional(func: Codeobjable) -> bool:
    '''
    :data:`True` only if the passed pure-Python callable accepts a variadic
    positional argument (e.g., ``*args``).

    Parameters
    ----------
    func : Union[Callable, CodeType, FrameType]
        Pure-Python callable, frame, or code object to be inspected.

    Returns
    ----------
    bool
        :data:`True` only if the passed callable accepts a variadic positional
        argument.

    Raises
    ----------
    _BeartypeUtilCallableException
         If the passed callable is *not* pure-Python.
    '''

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with the iter_func_args() iterator.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Code object underlying the passed pure-Python callable unwrapped.
    func_codeobj = get_func_codeobj(func=func, is_unwrap=False)

    # Return true only if this callable declares variadic positional arguments.
    return func_codeobj.co_flags & CO_VARARGS != 0


def is_func_arg_variadic_keyword(func: Codeobjable) -> bool:
    '''
    :data:`True` only if the passed pure-Python callable accepts a variadic
    keyword argument (e.g., ``**kwargs``).

    Parameters
    ----------
    func : Codeobjable
        Pure-Python callable, frame, or code object to be inspected.

    Returns
    ----------
    bool
        :data:`True` only if the passed callable accepts a variadic keyword
        argument.

    Raises
    ----------
    _BeartypeUtilCallableException
         If the passed callable is *not* pure-Python.
    '''

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize with the iter_func_args() iterator.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Code object underlying the passed pure-Python callable unwrapped.
    func_codeobj = get_func_codeobj(func=func, is_unwrap=False)

    # Return true only if this callable declares variadic keyword arguments.
    return func_codeobj.co_flags & CO_VARKEYWORDS != 0

# ....................{ TESTERS ~ name                     }....................
#FIXME: *THIS TESTER IS HORRIFYINGLY SLOW*, thanks to a naive implementation
#deferring to the slow iter_func_args() iterator. A substantially faster
#get_func_arg_names() getter should be implemented instead and this tester
#refactored to call that getter. How? Simple:
#    def get_func_arg_names(func: Callable) -> Tuple[str]:
#        # A trivial algorithm for deciding the number of arguments can be
#        # found at the head of the iter_func_args() iterator.
#        args_len = ...
#
#        # One-liners for great glory.
#        return func.__code__.co_varnames[:args_len] # <-- BOOM
def is_func_arg_name(func: Callable, arg_name: str) -> bool:
    '''
    :data:`True` only if the passed pure-Python callable accepts an argument
    with the passed name.

    Caveats
    ----------
    **This tester exhibits worst-case time complexity** ``O(n)`` **for** ``n``
    **the total number of arguments accepted by this callable,** due to
    unavoidably performing a linear search for an argument with this name is
    this callable's argument list. This tester should thus be called sparingly
    and certainly *not* repeatedly for the same callable.

    Parameters
    ----------
    func : Callable
        Pure-Python callable to be inspected.
    arg_name : str
        Name of the argument to be searched for.

    Returns
    ----------
    bool
        :data:`True` only if that callable accepts an argument with this name.

    Raises
    ----------
    _BeartypeUtilCallableException
         If the passed callable is *not* pure-Python.
    '''
    assert isinstance(arg_name, str), f'{arg_name} not string.'

    # Return true only if...
    return any(
        # This is the passed name...
        arg_meta[ARG_META_INDEX_NAME] == arg_name
        # For the name of any parameter accepted by this callable.
        for arg_meta in iter_func_args(func)
    )
