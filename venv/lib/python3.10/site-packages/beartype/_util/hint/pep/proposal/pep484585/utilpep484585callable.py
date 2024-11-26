#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **callable type hint
utilities** (i.e., callables generically applicable to both :pep:`484`- and
:pep:`585`-compliant ``Callable[...]`` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
import beartype.typing as typing
from beartype.roar import BeartypeDecorHintPep484585Exception
from beartype.typing import (
    TYPE_CHECKING,
    Union,
)
from beartype._data.hint.datahinttyping import TypeException
from beartype._data.hint.pep.sign.datapepsigns import HintSignCallable
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_CALLABLE_PARAMS)
from beartype._data.kind.datakindsequence import TUPLE_EMPTY
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10

# ....................{ HINTS                              }....................
# If an external static type checker (e.g., "mypy") is currently subjecting
# "beartype" to static analysis, reduce this hint to a simplistic facsimile of
# its full form tolerated by static type checkers.
if TYPE_CHECKING:
    _HINT_PEP484585_CALLABLE_PARAMS = Union[
        # For hints of the form "Callable[[{arg_hints}], {return_hint}]".
        tuple,
        # For hints of the form "Callable[typing.ParamSpec[...], {return_hint}]".
        typing.ParamSpec
    ]
# Else, expand this hint to its full form supported by runtime type checkers.
else:
    _HINT_PEP484585_CALLABLE_PARAMS = Union[
        # For hints of the form "Callable[[{arg_hints}], {return_hint}]".
        tuple,
        # For hints of the form "Callable[..., {return_hint}]".
        type(Ellipsis),
        # If the active Python interpreter targets Python >= 3.10, a union
        # additionally matching the PEP 612-compliant "ParamSpec" type.
        (
            # For hints of the form "Callable[typing.ParamSpec[...], {return_hint}]".
            typing.ParamSpec
            if IS_PYTHON_AT_LEAST_3_10 else
            # Else, the active Python interpreter targets Python < 3.10. In this
            # case, a meaninglessly redundant type listed above reducing to a noop.
            tuple
        )
    ]
    '''
    PEP-compliant type hint matching the first argument originally subscripting
    a :pep:`484`- or :pep:`585`-compliant **callable type hint** (i.e.,
    ``typing.Callable[...]`` or ``collections.abc.Callable[...]`` type hint).
    '''

# ....................{ VALIDATORS                         }....................
def _die_unless_hint_pep484585_callable(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is either a :pep:`484`- or
    :pep:`585`-compliant **callable type hint** (i.e., ``typing.Callable[...]``
    or ``collections.abc.Callable[...]`` type hint).

    Parameters
    ----------
    hint : object
        Object to be validated.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    :exc:`exception_cls`
        If this hint is either:

        * PEP-compliant but *not* uniquely identifiable by a sign.
        * PEP-noncompliant.
        * *Not* a hint (i.e., neither PEP-compliant nor -noncompliant).
        * *Not* a callable type hint (i.e., ``typing.Callable[...]`` or
          ``collections.abc.Callable[...]``).
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign

    # Sign uniquely identifying this hint if any *OR* raise an exception.
    hint_sign = get_hint_pep_sign(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # If this object is *NOT* a callable type hint, raise an exception.
    if hint_sign is not HintSignCallable:
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception class.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not '
            f'PEP 484 or 585 callable type hint '
            f'(i.e., "typing.Callable[...]" or '
            f'"collections.abc.Callable[...]").'
        )
    # Else, this object is a callable type hint, raise an exception.

# ....................{ GETTERS                            }....................
def get_hint_pep484585_callable_params(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> _HINT_PEP484585_CALLABLE_PARAMS:
    '''
    Object describing all **parameter type hints** (i.e., PEP-compliant child
    type hints typing the parameters accepted by a passed or returned callable)
    of the passed **callable type hint** (i.e., :pep:`484`-compliant
    ``typing.Callable[...]`` or :pep:`585`-compliant
    ``collections.abc.Callable[...]`` type hint).

    This getter returns one of several different types of objects, conditionally
    depending on the type of the first argument originally subscripting this
    hint. Specifically, if this hint was of the form:

    * ``Callable[[{arg_hints}], {return_hint}]``, this getter returns a tuple of
      the zero or more parameter type hints subscripting (indexing) this hint.
    * ``Callable[..., {return_hint}]``, the :data:`Ellipsis` singleton.
    * ``Callable[typing.ParamSpec[...], {return_hint}]``, the
      ``typing.ParamSpec[...]`` subscripting (indexing) this hint.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation requires no
    iteration and thus exhibits guaranteed constant-time behaviour.

    Parameters
    ----------
    hint : object
        Callable type hint to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :exc:`.BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    ----------
    _HINT_PEP484585_CALLABLE_PARAMS
        First argument originally subscripting this hint.

    Raises
    ----------
    exception_cls
        If this hint is *not* a callable type hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_args,
        get_hint_pep_sign_or_none,
    )

    # If this hint is *NOT* a callable type hint, raise an exception.
    _die_unless_hint_pep484585_callable(hint)
    # Else, this hint is a callable type hint.

    # Flattened tuple of the one or more child type hints subscripting this
    # callable type hint. Presumably for space efficiency reasons, both PEP 484-
    # *AND* 585-compliant callable type hints implicitly flatten the "__args__"
    # dunder tuple from the original data structure subscripting those hints.
    # CPython produces this flattened tuple as the concatenation of:
    #
    # * Either:
    #   * If the first child type originally subscripting this hint was a list,
    #     all items subscripting the nested list of zero or more parameter type
    #     hints originally subscripting this hint as is: e.g.,
    #         >>> Callable[[], bool].__args__
    #         (bool,)
    #         >>> Callable[[int, str], bool].__args__
    #         (int, str, bool)
    #
    #     This includes a list containing only the empty tuple signifying a
    #     callable accepting *NO* parameters, in which case that empty tuple is
    #     preserved as is: e.g.,
    #         >>> Callable[[()], bool].__args__
    #         ((), bool)
    #   * Else, the first child type originally subscripting this hint as is. In
    #     this case, that child type is required to be either:
    #     * An ellipsis object (i.e., the "Ellipsis" builtin singleton): e.g.,
    #         >>> Callable[..., bool].__args__
    #         (Ellipsis, bool)
    #     * A PEP 612-compliant parameter specification (i.e.,
    #       "typing.ParamSpec[...]" type hint): e.g.,
    #         >>> Callable[ParamSpec('P'), bool].__args__
    #         (~P, bool)
    #     * A PEP 612-compliant parameter concatenation (i.e.,
    #       "typing.Concatenate[...]" type hint): e.g.,
    #         >>> Callable[Concatenate[str, ParamSpec('P')], bool].__args__
    #         (typing.Concatenate[str, ~P], bool)
    # * The return type hint originally subscripting this hint.
    #
    # Note that both PEP 484- *AND* 585-compliant callable type hints guarantee
    # this tuple to contain at least one child type hint. Ergo, we avoid
    # validating that constraint here: e.g.,
    #     >>> from typing import Callable
    #     >>> Callable[()]
    #     TypeError: Callable must be used as Callable[[arg, ...], result].
    #     >>> from collections.abc import Callable
    #     >>> Callable[()]
    #     TypeError: Callable must be used as Callable[[arg, ...], result].
    hint_args = get_hint_pep_args(hint)

    # Number of parameter type hints flattened into this tuple, calculated by
    # excluding the trailing return type hint also flattened into this tuple.
    #
    # Note that by the above constraint, this number is guaranteed to be
    # non-negative: e.g.,
    #     >>> hint_args_len >= 0
    #     True
    hint_params_len = len(hint_args) - 1

    # If this callable type hint was subscripted by *NO* parameter type hints,
    # return the empty tuple for efficiency.
    if hint_params_len == 0:
        return ()
    # Else, this callable type hint was subscripted by one or more parameter
    # type hints.
    #
    # If this callable type hint was subscripted by two or more parameter type
    # hints, this callable type hint *CANNOT* have been subscripted by a single
    # "special" parameter type hint (e.g., ellipsis, parameter specification).
    # By elimination, the only remaining category of parameter type hint is a
    # nested list of two or more parameter type hints. In this case, return the
    # tuple slice containing the parameter type hints omitting the trailing
    # return type hint.
    elif hint_params_len >= 2:
        return hint_args[:-1]
    # Else, this callable type hint was subscripted by exactly one parameter
    # type hint... which could be either a nested list of one or more parameter
    # type hints *OR* a "special" parameter type hint. To differentiate the
    # former from the latter, we explicitly detect all possible instances of the
    # latter and only fallback to the former after exhausting the latter.

    # Single parameter type hint subscripting this callable type hint.
    hint_param = hint_args[0]

    # If this parameter type hint is either...
    #
    # Note that we intentionally avoid attempting to efficiently test this
    # parameter type hint against a set (e.g., "hint_param in {..., ()}"). This
    # parameter type hint is *NOT* guaranteed to be hashable and thus testable
    # against a hash-based collection.
    if (
        # An ellipsis, return an ellipsis.
        hint_param is ... or
        # The empty tuple, reduce this unlikely (albeit possible) edge case
        # to the empty tuple returned for the more common case of a callable
        # type hint subscripted by an empty list. That is, reduce these two
        # cases to the same empty tuple for simplicity: e.g.,
        #     >>> Callable[[], bool].__args__
        #     (bool,)  # <------ this is good
        #     >>> Callable[[()], bool].__args__
        #     ((), bool,)  # <-- this is bad, so pretend this never happens
        hint_param is TUPLE_EMPTY
    ):
        return hint_param
    # Else, this parameter type hint is neither the empty tuple *NOR* an
    # ellipsis.

    # Sign uniquely identifying this parameter type hint if any *OR* "None".
    hint_param_sign = get_hint_pep_sign_or_none(hint_param)

    # If this parameter type hint is a PEP-compliant parameter type (i.e.,
    # uniquely identifiable by a sign), return this hint as is.
    #
    # Note that:
    # * This requires callers to handle all possible categories of
    #   PEP-compliant parameter type hints -- including both
    #   "typing.ParamSpec[...]" and "typing.Concatenate[...]" parameter type
    #   hints, presumably by (...somewhat redundantly, but what can you do)
    #   calling the get_hint_pep_sign_or_none() getter themselves.
    # * Both PEP 484- *AND* 585-compliant callable type hints guarantee
    #   this parameter type hint to be constrained to the subset of
    #   PEP-compliant parameter type hints. Arbitrary parameter type hints
    #   are prohibited. Ergo, we avoid validating that constraint here:
    #   e.g.,
    #     >>> from typing import Callable, List
    #     >>> Callable[List[int], bool]
    #     TypeError: Callable[args, result]: args must be a list. Got
    #     typing.List[int]
    if hint_param_sign in HINT_SIGNS_CALLABLE_PARAMS:
        return hint_param
    # Else, this parameter type hint is *NOT* a PEP-compliant parameter type
    # hint. This hint *CANNOT* be "special" and *MUST* thus be the single
    # parameter type hint of a nested list: e.g.,
    #     >>> Callable[[list[int]], bool].__args__
    #     (list[int], bool)

    # In this case, return the 1-tuple containing exactly this hint.
    # print(f'get_hint_pep484585_callable_params({repr(hint)}) == ({repr(hint_param)},)')
    # print(f'{repr(hint_param)} sign: {repr(hint_param_sign)}')
    return (hint_param,)


def get_hint_pep484585_callable_return(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
    exception_prefix: str = '',
) -> object:
    '''
    **Return type hint** (i.e., PEP-compliant child type hint typing the return
    returned by a passed or returned callable) of the passed
    **callable type hint** (i.e., :pep:`484`-compliant ``typing.Callable[...]``
    or :pep:`585`-compliant ``collections.abc.Callable[...]`` type hint).

    This getter is considerably more trivial than the companion
    :func:`get_hint_pep484585_callable_params` getter. Although this getter
    exists largely for orthogonality and completeness, callers are advised to
    defer to this getter rather than access this return type hint directly.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Callable type hint to be inspected.
    exception_cls : TypeException, optional
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep484585Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    ----------
    object
        Last argument originally subscripting this hint.

    Raises
    ----------
    :exc:`exception_cls`
        If this hint is *not* a callable type hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args

    # If this hint is *NOT* a callable type hint, raise an exception.
    _die_unless_hint_pep484585_callable(hint)
    # Else, this hint is a callable type hint.

    # Flattened tuple of the one or more child type hints subscripting this
    # callable type hint. See get_hint_pep484585_callable_params() for details.
    hint_args = get_hint_pep_args(hint)

    # Return the last object subscripting this hint.
    #
    # Note that both the PEP 484-compliant "typing.Callable" factory *AND* the
    # PEP 585-compliant "collections.abc.Callable" factory guarantee this object
    # to exist. Ergo, we intentionally avoid repeating any validation here:
    #     $ python3.10
    #     >>> from collections.abc import Callable
    #     >>> Callable[()]
    #     TypeError: Callable must be used as Callable[[arg, ...], result].
    return hint_args[-1]
