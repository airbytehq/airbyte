#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`557`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep557Exception
from beartype._data.hint.datahinttyping import TypeException
from beartype._data.hint.pep.sign.datapepsigns import HintSignDataclassInitVar

# ....................{ GETTERS                            }....................
def get_hint_pep557_initvar_arg(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep557Exception,
    exception_prefix: str = '',
) -> object:
    '''
    PEP-compliant child type hint subscripting the passed :pep:`557`-compliant
    **dataclass initialization-only instance variable type hint** (i.e.,
    subscription of the :class:`dataclasses.InitVar` type hint factory).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep557Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    ----------
    object
        PEP-compliant child type hint subscripting this parent type hint.

    Raises
    ----------
    BeartypeDecorHintPep557Exception
        If this object is *not* a dataclass initialization-only instance
        variable type hint.
    '''
    
    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none

    # Sign uniquely identifying this hint if this hint is identifiable *OR*
    # "None" otherwise.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # If this hint is *NOT* a dataclass initialization-only instance variable
    # type hint, raise an exception.
    if hint_sign is not HintSignDataclassInitVar:
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not '
            f'PEP 557-compliant "dataclasses.TypeVar" instance.'
        )
    # Else, this hint is such a hint.

    # Return the child type hint subscripting this parent type hint. Yes, this
    # hint exposes this child via a non-standard instance variable rather than
    # the "__args__" dunder tuple standardized by PEP 484.
    return hint.type  # type: ignore[attr-defined]

# ....................{ REDUCERS                           }....................
def reduce_hint_pep557_initvar(
    hint: object, exception_prefix: str, *args, **kwargs) -> object:
    '''
    Reduce the passed :pep:`557`-compliant **dataclass initialization-only
    instance variable type hint** (i.e., subscription of the
    :class:`dataclasses.InitVar` type hint factory) to the child type hint
    subscripting this parent hint -- which is otherwise functionally useless
    from the admittedly narrow perspective of runtime type-checking.

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Type variable to be reduced.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    All remaining passed arguments are silently ignored.

    Returns
    ----------
    object
        Lower-level type hint currently supported by :mod:`beartype`.
    '''

    # Reduce this "typing.InitVar[{hint}]" type hint to merely "{hint}".
    return get_hint_pep557_initvar_arg(
        hint=hint, exception_prefix=exception_prefix)
