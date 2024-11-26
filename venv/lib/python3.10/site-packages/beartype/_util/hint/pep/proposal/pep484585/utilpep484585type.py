#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **dual type hint utilities**
(i.e., callables generically applicable to both :pep:`484`- and
:pep:`585`-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484585Exception
from beartype.typing import (
    # Any,
    Tuple,
    TypeVar,
    Union,
)
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignForwardRef,
    HintSignType,
    HintSignUnion,
)
from beartype._util.cls.pep.utilpep3119 import (
    die_unless_type_issubclassable,
    die_unless_type_or_types_issubclassable,
)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585arg import (
    get_hint_pep484585_args_1)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585ref import (
    Pep484585ForwardRef)
from typing import (
    Type as typing_Type,  # <-- intentional to distinguish from "type" below
)

# ....................{ HINTS ~ private                    }....................
_HINT_PEP484585_SUBCLASS_ARGS_1_UNION = Union[
    type, Tuple[type], TypeVar, Pep484585ForwardRef,]
'''
Union of the types of all permissible :pep:`484`- or :pep:`585`-compliant
**subclass type hint arguments** (i.e., PEP-compliant child type hints
subscripting (indexing) a subclass type hint).
'''

# ....................{ GETTERS                            }....................
def get_hint_pep484585_type_superclass(
    hint: object,
    exception_prefix: str,
) -> _HINT_PEP484585_SUBCLASS_ARGS_1_UNION:
    '''
    **Issubclassable superclass(es)** (i.e., class whose metaclass does *not*
    define a ``__subclasscheck__()`` dunder method that raises an exception,
    tuple of such classes, or forward reference to such a class) subscripting
    the passed :pep:`484`- or :pep:`585`-compliant **subclass type hint**
    (i.e., hint constraining objects to subclass that superclass).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    ----------
    _HINT_PEP484585_SUBCLASS_ARGS_1_UNION
        Argument subscripting this subclass type hint, guaranteed to be either:

        * An issubclassable class.
        * A tuple of issubclassable classes.
        * A :pep:`484`-compliant forward reference to an issubclassable class
          that typically has yet to be declared (i.e.,
          :class:`typing.ForwardRef` instance).
        * A :pep:`484`-compliant type variable constrained to classes (i.e.,
          :class:`typing.TypeVar` instance).
        * A :pep:`585`-compliant union of two or more issubclassable classes.
        * A :pep:`484`-compliant type variable constrained to classes (i.e.,
          :class:`typing.TypeVar` instance).

    Raises
    ----------
    BeartypeDecorHintPep3119Exception
        If this superclass subscripting this type hint is *not*
        **issubclassable** (i.e., class whose metaclass defines a
        ``__subclasscheck__()`` dunder method raising an exception).
    BeartypeDecorHintPep484585Exception
        If this hint is either:

        * Neither a :pep:`484`- nor :pep:`585`-compliant subclass type hint.
        * A :pep:`484`- or :pep:`585`-compliant subclass type hint subscripted
          by one argument that is neither a class, union of classes, nor
          forward reference to a class.
    BeartypeDecorHintPep585Exception
        If this hint is either:

        * A :pep:`585`-compliant subclass type hint subscripted by either:

          * *No* arguments.
          * Two or more arguments.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_args,
        get_hint_pep_sign,
        get_hint_pep_sign_or_none,
    )

    # If this is neither a PEP 484- *NOR* PEP 585-compliant subclass type hint,
    # raise an exception.
    if get_hint_pep_sign(hint) is not HintSignType:
        raise BeartypeDecorHintPep484585Exception(
            f'{exception_prefix}{repr(hint)} '
            f'neither PEP 484 nor 585 subclass type hint.'
        )
    # Else, this is a subclass type hint.

    # Superclass subscripting this hint.
    hint_superclass = get_hint_pep484585_args_1(
        hint=hint, exception_prefix=exception_prefix)

    # Sign identifying this superclass.
    hint_superclass_sign = get_hint_pep_sign_or_none(hint_superclass)

    # If this superclass is actually a union of superclasses...
    if hint_superclass_sign is HintSignUnion:
        # Efficiently reduce this superclass to the tuple of superclasses
        # subscripting and thus underlying this union.
        hint_superclass = get_hint_pep_args(hint_superclass)

        # If any item of this tuple is *NOT* an issubclassable class, raise an
        # exception.
        # print(f'hint_superclass union arg: {hint_superclass}')
        die_unless_type_or_types_issubclassable(
            type_or_types=hint_superclass, exception_prefix=exception_prefix)  # type: ignore[arg-type]
    # Else, this superclass is *NOT* a union of superclasses.
    #
    # If this superclass is actually a forward reference to a superclass,
    # silently accept this reference as is. This conditional exists only to
    # avoid raising a subsequent exception.
    elif hint_superclass_sign is HintSignForwardRef:
        pass
    # Else, this superclass is *NOT* a forward reference to a superclass.
    #
    # If this superclass is a class...
    elif isinstance(hint_superclass, type):
        die_unless_type_issubclassable(
            cls=hint_superclass, exception_prefix=exception_prefix)
        # Else, this superclass is issubclassable.
    # Else, this superclass is of an unexpected type. In this case, raise an
    # exception.
    #
    # Note that PEP 585-compliant subclass type hints infrequently trigger this
    # edge case. Although the "typing" module explicitly validates the
    # arguments subscripting PEP 484-compliant type hints, the CPython
    # interpreter applies *NO* such validation to PEP 585-compliant subclass
    # type hints. For example, PEP 585-compliant subclass type hints are
    # subscriptable by the empty tuple, which is technically an argument:
    #     >>> type[()].__args__
    #     ()   # <---- thanks fer nuthin
    else:
        raise BeartypeDecorHintPep484585Exception(
            f'{exception_prefix}PEP 484 or 585 subclass type hint '
            f'{repr(hint)} child type hint {repr(hint_superclass)} neither '
            f'class, union of classes, nor forward reference to class.'
        )

    # Return this superclass.
    return hint_superclass  # type: ignore[return-value]

# ....................{ REDUCERS                           }....................
#FIXME: Unit test us up.
def reduce_hint_pep484585_type(
    hint: object, exception_prefix: str, *args, **kwargs) -> object:
    '''
    Reduce the passed :pep:`484`- or :pep:`585`-compliant **subclass type
    hint** (i.e., hint constraining objects to subclass that superclass) to the
    :class:`type` superclass if that hint is subscripted by an ignorable child
    type hint (e.g., :attr:`typing.Any`, :class:`type`) *or* preserve this hint
    as is otherwise (i.e., if that hint is *not* subscripted by an ignorable
    child type hint).

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Subclass type hint to be reduced.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    All remaining passed arguments are silently ignored.

    Raises
    ----------
    BeartypeDecorHintPep484585Exception
        If this hint is neither a :pep:`484`- nor :pep:`585`-compliant subclass
        type hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.utilhinttest import is_hint_ignorable

    # If this hint is the unsubscripted PEP 484-compliant subclass type hint,
    # immediately reduce this hint to the "type" superclass.
    #
    # Note that this is *NOT* merely a nonsensical optimization. The
    # implementation of the unsubscripted PEP 484-compliant subclass type hint
    # significantly differs across Python versions. Under some but *NOT* all
    # supported Python versions (notably, Python 3.7 and 3.8), the "typing"
    # module subversively subscripts this hint by a type variable; under all
    # others, this hint remains unsubscripted. In the latter case, passing this
    # hint to the subsequent get_hint_pep484585_args_1() would erroneously
    # raise an exception.
    if hint is typing_Type:
        return type
    # Else, this hint is *NOT* the unsubscripted PEP 484-compliant subclass
    # type hint.

    # Superclass subscripting this hint.
    #
    # Note that we intentionally do *NOT* call the high-level
    # get_hint_pep484585_type_superclass() getter here, as the
    # validation performed by that function would raise exceptions for
    # various child type hints that are otherwise permissible (e.g.,
    # "typing.Any").
    hint_superclass = get_hint_pep484585_args_1(
        hint=hint, exception_prefix=exception_prefix)

    # If this argument is either...
    if (
        # An ignorable type hint (e.g., "typing.Any") *OR*...
        is_hint_ignorable(hint_superclass) or
        # The "type" superclass, which is effectively ignorable in this
        # context of subclasses, as *ALL* classes necessarily subclass
        # that superclass.
        hint_superclass is type
    ):
        # Reduce this subclass type hint to the "type" superclass.
        hint = type
    # Else, this argument is unignorable and thus irreducible.

    # Return this possibly reduced type hint.
    return hint
