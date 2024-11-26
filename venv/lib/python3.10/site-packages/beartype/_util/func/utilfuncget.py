#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable getters** (i.e., utility functions dynamically
querying and retrieving various properties of passed callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype.typing import (
    Any,
    Callable,
    Optional,
)
from beartype._data.hint.datahinttyping import (
    HintAnnotations,
    TypeException,
)

# ....................{ GETTERS ~ hints                    }....................
#FIXME: Refactor all unsafe access of the low-level "__annotations__" dunder
#attribute to instead call this high-level getter, please.
#FIXME: Unit test us up, please.
def get_func_annotations(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> HintAnnotations:
    '''
    **Annotations** (i.e., dictionary mapping from the name of each annotated
    parameter or return of the passed pure-Python callable to the type hint
    annotating that parameter or return) of that callable.

    Parameters
    ----------
    func : object
        Object to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`._BeartypeUtilCallableException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    HintAnnotations
        Annotations of that callable.

    Raises
    ----------
    exception_cls
         If that callable is *not* actually a pure-Python callable.

    See Also
    ----------
    :func:`.get_func_annotations_or_none`
        Further details.
    '''

    # Annotations of that callable if that callable is actually a pure-Python
    # callable *OR* "None" otherwise.
    hint_annotations = get_func_annotations_or_none(func)

    # If that callable is *NOT* pure-Python, raise an exception.
    if hint_annotations is None:
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # If that callable is uncallable, raise an appropriate exception.
        if not callable(func):
            raise exception_cls(f'{exception_prefix}{repr(func)} not callable.')
        # Else, that callable is callable.

        # Raise a human-readable exception.
        raise exception_cls(
            f'{exception_prefix}{repr(func)} not pure-Python function.')
    # Else, that callable is pure-Python.

    # Return these annotations.
    return hint_annotations


#FIXME: Refactor all unsafe access of the low-level "__annotations__" dunder
#attribute to instead call this high-level getter, please.
#FIXME: Unit test us up, please.
def get_func_annotations_or_none(func: Callable) -> Optional[HintAnnotations]:
    '''
    **Annotations** (i.e., dictionary mapping from the name of each annotated
    parameter or return of the passed pure-Python callable to the type hint
    annotating that parameter or return) of that callable if that callable is
    actually a pure-Python callable *or* :data:`None` otherwise (i.e., if that
    callable is *not* a pure-Python callable).

    Parameters
    ----------
    func : object
        Object to be inspected.

    Returns
    ----------
    Optional[HintAnnotations]
        Either:

        * If that callable is actually a pure-Python callable, the annotations
          of that callable.
        * Else, :data:`None`.
    '''

    # Demonstrable monstrosity demons!
    #
    # Note that the "__annotations__" dunder attribute is guaranteed to exist
    # *ONLY* for standard pure-Python callables. Various other callables of
    # interest (e.g., functions exported by the standard "operator" module) do
    # *NOT* necessarily declare that attribute. Since this tester is commonly
    # called in general-purpose contexts where this guarantee does *NOT*
    # necessarily hold, we intentionally access that attribute safely albeit
    # somewhat more slowly via getattr().
    return getattr(func, '__annotations__', None)

# ....................{ GETTERS ~ descriptor               }....................
def get_func_classmethod_wrappee(
    # Mandatory parameters.
    func: Any,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> Callable:
    '''
    Pure-Python unbound function wrapped by the passed **C-based unbound class
    method descriptor** (i.e., method decorated by the builtin
    :class:`classmethod` decorator, yielding a non-callable instance of that
    :class:`classmethod` decorator class implemented in low-level C and
    accessible via the low-level :attr:`object.__dict__` dictionary rather than
    as class or instance attributes).

    Parameters
    ----------
    func : object
        Object to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :static:`_BeartypeUtilCallableException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    Callable
        Pure-Python unbound function wrapped by this class method descriptor.

    Raises
    ----------
    exception_cls
         If the passed object is *not* a class method descriptor.

    See Also
    ----------
    :func:`beartype._util.func.utilfunctest.is_func_classmethod`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunctest import die_unless_func_classmethod

    # If this object is *NOT* a class method descriptor, raise an exception.
    die_unless_func_classmethod(
        func=func,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this object is a class method descriptor.

    # Return the pure-Python function wrapped by this descriptor. Just do it!
    return func.__func__


def get_func_staticmethod_wrappee(
    # Mandatory parameters.
    func: Any,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> Callable:
    '''
    Pure-Python unbound function wrapped by the passed **C-based unbound static
    method descriptor** (i.e., method decorated by the builtin
    :class:`staticmethod` decorator, yielding a non-callable instance of that
    :class:`staticmethod` decorator class implemented in low-level C and
    accessible via the low-level :attr:`object.__dict__` dictionary rather than
    as class or instance attributes).

    Parameters
    ----------
    func : object
        Object to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :static:`_BeartypeUtilCallableException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    Callable
        Pure-Python unbound function wrapped by this static method descriptor.

    Raises
    ----------
    exception_cls
         If the passed object is *not* a static method descriptor.

    See Also
    ----------
    :func:`beartype._util.func.utilfunctest.is_func_staticmethod`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunctest import die_unless_func_staticmethod

    # If this object is *NOT* a static method descriptor, raise an exception.
    die_unless_func_staticmethod(
        func=func,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this object is a static method descriptor.

    # Return the pure-Python function wrapped by this descriptor. Just do it!
    return func.__func__
