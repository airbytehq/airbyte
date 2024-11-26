#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`586`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep586Exception
from beartype.typing import Any
from beartype._cave._cavefast import EnumMemberType, NoneType
from beartype._data.hint.datahinttyping import TypeException
from beartype._data.hint.pep.sign.datapepsigns import HintSignLiteral
from beartype._util.text.utiltextjoin import join_delimited_disjunction_types

# ....................{ CONSTANTS                          }....................
_LITERAL_ARG_TYPES = (bool, bytes, int, str, EnumMemberType, NoneType)
'''
Tuple of all types of objects permissible as arguments subscripting the
:pep:`586`-compliant :attr:`typing.Literal` singleton.

These types are explicitly listed by :pep:`586` as follows:

    Literal may be parameterized with literal ints, byte and unicode strings,
    bools, Enum values and None.
'''

# ....................{ VALIDATORS                         }....................
def die_unless_hint_pep586(
    # Mandatory parameters.
    hint: Any,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep586Exception,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception of the passed type unless the passed object is a
    :pep:`586`-compliant type hint (i.e., subscription of either the
    :attr:`typing.Literal` or :attr:`typing_extensions.Literal` type hint
    factories).

    Ideally, the :attr:`typing.Literal` singleton would internally validate the
    literal objects subscripting that singleton at subscription time (i.e., in
    the body of the ``__class_getitem__()`` dunder method). Whereas *all* other
    :mod:`typing` attributes do just that, :attr:`typing.Literal` permissively
    accepts all possible arguments like a post-modern philosopher hopped up on
    too much tenure. For inexplicable reasons, :pep:`586` explicitly requires
    third-party type checkers (that's us) to validate these hints rather than
    standardizing that validation in the :mod:`typing` module. Weep, Guido!

    Caveats
    ----------
    **This function is slow** and should thus be called only once per
    visitation of a :pep:`586`-compliant type hint. Specifically, this function
    is O(n) for n the number of arguments subscripting this hint.

    Parameters
    ----------
    hint : object
        Object to be inspected.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep586Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Raises
    ----------
    :exc:`exception_cls`
        If this object either:

        * Is *not* a subscription of either the :attr:`typing.Literal` or
          :attr:`typing_extensions.Literal` type hint factories.
        * Subscripts either factory with zero arguments via the empty tuple,
          which these factories sadly fails to guard against.
        * Subscripts either factory with one or more arguments that are *not*
          **valid literals**, defined as the set of all:

          * Booleans.
          * Byte strings.
          * Integers.
          * Unicode strings.
          * :class:`enum.Enum` members.
          * The ``None`` singleton.
    '''

    # Tuple of zero or more literal objects subscripting this hint.
    hint_literals = get_hint_pep586_literals(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # If the caller maliciously subscripted this hint by the empty tuple and
    # thus *NO* arguments, raise an exception. Ideally, the "typing.Literal"
    # singleton would guard against this itself. It does not; thus, we do.
    if not hint_literals:
        raise exception_cls(
            f'{exception_prefix}PEP 586 type hint {repr(hint)} '
            f'subscripted by empty tuple.'
        )

    # If any argument subscripting this hint is *NOT* a valid literal...
    #
    # Sadly, despite PEP 586 imposing strict restrictions on the types of
    # objects permissible as arguments subscripting the "typing.Literal"
    # singleton, PEP 586 explicitly offloads the odious chore of enforcing
    # those restrictions onto third-party type checkers by intentionally
    # implementing that singleton to permissively accept *ALL* possible
    # objects when subscripted:
    #     Although the set of parameters Literal[...] may contain at type
    #     check time is very small, the actual implementation of
    #     typing.Literal will not perform any checks at runtime.
    if any(
        not isinstance(hint_literal, _LITERAL_ARG_TYPES)
        for hint_literal in hint_literals
    # Then raise a human-readable exception describing this invalidity.
    ):
        # For each argument subscripting this hint...
        for hint_literal_index, hint_literal in enumerate(hint_literals):
            # If this argument is invalid as a literal argument...
            if not isinstance(hint_literal, _LITERAL_ARG_TYPES):
                # Human-readable concatenation of the types of all valid
                # literal arguments, delimited by commas and/or "or".
                hint_literal_types = join_delimited_disjunction_types(
                    _LITERAL_ARG_TYPES)

                # Raise an exception.
                raise exception_cls(
                    f'{exception_prefix}PEP 586 type hint {repr(hint)} '
                    f'argument {hint_literal_index} '
                    f'{repr(hint_literal)} not {hint_literal_types}.'
                )

# ....................{ GETTERS                            }....................
def get_hint_pep586_literals(
    # Mandatory parameters.
    hint: Any,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep586Exception,
    exception_prefix: str = '',
) -> tuple:
    '''
    Tuple of zero or more literal objects subscripting the passed
    :pep:`586`-compliant type hint (i.e., subscription of either the
    :attr:`typing.Literal` or :attr:`typing_extensions.Literal` type hint
    factories).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **This low-level getter performs no validation of the contents of this
    tuple.** Consider calling the high-level :func:`die_unless_hint_pep586`
    validator to do so before leveraging this tuple elsewhere.

    Parameters
    ----------
    hint : object
        :pep:`586`-compliant type hint to be inspected.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep586Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    ----------
    tuple
        Tuple of zero or more literal objects subscripting this hint.

    Raises
    ----------
    :exc:`exception_cls`
        If this object is *not* a :pep:`586`-compliant type hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign

    # If this hint is *NOT* PEP 586-compliant, raise an exception.
    if get_hint_pep_sign(hint) is not HintSignLiteral:
        raise exception_cls(
            f'{exception_prefix}PEP 586 type hint {repr(hint)} neither '
            f'"typing.Literal" nor "typing_extensions.Literal".'
        )
    # Else, this hint is PEP 586-compliant.

    # Return the standard tuple of all literals subscripting this hint.
    return hint.__args__
