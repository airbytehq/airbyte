#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype class type hint violation describers** (i.e., functions returning
human-readable strings explaining violations of type hints that are standard
isinstanceable classes rather than PEP-specific objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeCallHintForwardRefException
from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
from beartype._cave._cavefast import TestableTypes
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignForwardRef,
    HintSignType,
)
from beartype._decor.error._errorcause import ViolationCause
from beartype._decor.error._util.errorutilcolor import color_hint
from beartype._util.cls.utilclstest import is_type_subclass
from beartype._util.cls.pep.utilpep3119 import (
    die_unless_type_isinstanceable,
    die_unless_type_issubclassable,
)
from beartype._util.hint.nonpep.utilnonpeptest import (
    die_unless_hint_nonpep_tuple)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585ref import (
    import_pep484585_forwardref_type_relative_to_object)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585type import (
    get_hint_pep484585_type_superclass)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_origin_type_isinstanceable_or_none)
from beartype._util.text.utiltextjoin import join_delimited_disjunction_types
from beartype._util.text.utiltextlabel import label_type
from beartype._decor.error._util.errorutiltext import represent_pith

# ....................{ GETTERS ~ instance : type          }....................
def find_cause_instance_type(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either is
    or is not an instance of the isinstanceable type of that cause.

    Parameters
    ----------
    cause : ViolationCause
        Input cause providing this data.

    Returns
    ----------
    ViolationCause
        Output cause type-checking this data.
    '''
    assert isinstance(cause, ViolationCause), f'{repr(cause)} not cause.'

    # If this hint is *NOT* an isinstanceable type, raise an exception.
    die_unless_type_isinstanceable(
        cls=cause.hint,
        exception_cls=_BeartypeCallHintPepRaiseException,
        exception_prefix=cause.exception_prefix,
    )
    # Else, this hint is an isinstanceable type.

    # Output cause to be returned, permuted from this input cause such that the
    # output cause justification is either...
    cause_return = cause.permute(cause_str_or_none=(
        # If this pith is an instance of this type, "None";
        None
        if isinstance(cause.pith, cause.hint) else
        # Else, this pith is *NOT* an instance of this type. In this case, a
        # human-readable string describing this failure.
        (
            f'{represent_pith(cause.pith)} not instance of '
            f'{color_hint(label_type(cause.hint))}'
        )
    ))

    # Return this output cause.
    return cause_return


def find_cause_instance_type_forwardref(
    cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either is
    or is not an instance of the class referred to by the **forward reference
    type hint** (i.e., string whose value is the name of a user-defined class
    which has yet to be defined) of that cause.

    Parameters
    ----------
    cause : ViolationCause
        Input cause providing this data.

    Returns
    ----------
    ViolationCause
        Output cause type-checking this data.
    '''
    assert isinstance(cause, ViolationCause), f'{repr(cause)} not cause.'
    assert cause.hint_sign is HintSignForwardRef, (
        f'{cause.hint_sign} not forward reference.')

    # Class referred to by this forward reference.
    hint_forwardref_type = import_pep484585_forwardref_type_relative_to_object(
        hint=cause.hint,
        obj=cause.func,
        exception_cls=BeartypeCallHintForwardRefException,
        exception_prefix=cause.exception_prefix,
    )

    # Defer to the function handling isinstanceable classes. Neato!
    return find_cause_instance_type(cause.permute(hint=hint_forwardref_type))


def find_cause_type_instance_origin(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either is
    or is not an instance of the isinstanceable type underlying the
    **originative type hint** (i.e., PEP-compliant type hint originating from a
    non-:mod:`typing` class) of that cause.

    Parameters
    ----------
    cause : ViolationCause
        Input cause providing this data.

    Returns
    ----------
    ViolationCause
        Output cause type-checking this data.
    '''
    assert isinstance(cause, ViolationCause), f'{repr(cause)} not cause.'

    # Isinstanceable origin type originating this hint if any *OR* "None".
    hint_type = get_hint_pep_origin_type_isinstanceable_or_none(cause.hint)

    # If this hint does *NOT* originate from such a type, raise an exception.
    if hint_type is None:
        raise _BeartypeCallHintPepRaiseException(
            f'{cause.exception_prefix}type hint '
            f'{repr(cause.hint)} not originated from '
            f'isinstanceable origin type.'
        )
    # Else, this hint originates from such a type.

    # Defer to the getter function handling non-"typing" classes. Presto!
    return find_cause_instance_type(cause.permute(hint=hint_type))

# ....................{ GETTERS ~ instance : types         }....................
def find_cause_instance_types_tuple(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either is
    or is not an instance of one or more isinstanceable types in the tuple of
    these types of that cause.

    Parameters
    ----------
    cause : ViolationCause
        Input cause providing this data.

    Returns
    ----------
    ViolationCause
        Output cause type-checking this data.
    '''
    assert isinstance(cause, ViolationCause), f'{repr(cause)} not cause.'

    # If this hint is *NOT* a tuple union, raise an exception.
    die_unless_hint_nonpep_tuple(
        hint=cause.hint,
        exception_prefix=cause.exception_prefix,
        exception_cls=_BeartypeCallHintPepRaiseException,
    )
    # Else, this hint is a tuple union.

    # Output cause to be returned, permuted from this input cause such that the
    # output cause justification is either...
    cause_return = cause.permute(cause_str_or_none=(
        # If this pith is an instance of one or more types in this tuple union,
        # "None";
        None
        if isinstance(cause.pith, cause.hint) else
        # Else, this pith is an instance of *NO* types in this tuple union. In
        # this case, a substring describing this failure to be embedded in a
        # longer string.
        (
            f'{represent_pith(cause.pith)} not instance of '
            f'{color_hint(join_delimited_disjunction_types(cause.hint))}'
        )
    ))

    # Return this cause.
    return cause_return

# ....................{ GETTERS ~ subclass : type          }....................
def find_cause_subclass_type(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either is
    or is not a subclass of the issubclassable type of that cause.

    Parameters
    ----------
    cause : ViolationCause
        Input cause providing this data.

    Returns
    ----------
    ViolationCause
        Output cause type-checking this data.
    '''
    assert isinstance(cause, ViolationCause), f'{repr(cause)} not cause.'
    assert cause.hint_sign is HintSignType, (
        f'{cause.hint_sign} not HintSignType.')

    # Superclass this pith is required to be a subclass of.
    hint_superclass = get_hint_pep484585_type_superclass(
        hint=cause.hint, exception_prefix=cause.exception_prefix)

    # If this superclass is neither a class nor tuple of classes, this
    # superclass *MUST* by process of elimination and the validation already
    # performed above by the get_hint_pep484585_type_superclass() getter be
    # a forward reference to a class. In this case...
    if not isinstance(hint_superclass, TestableTypes):
        # Reduce this superclass to the class referred to by this forward
        # reference.
        hint_superclass = import_pep484585_forwardref_type_relative_to_object(
            hint=hint_superclass,  # type: ignore[arg-type]
            obj=cause.func,
            exception_cls=BeartypeCallHintForwardRefException,
            exception_prefix=cause.exception_prefix,
        )

        # If this superclass is *NOT* issubclassable, raise an exception.
        die_unless_type_issubclassable(
            cls=hint_superclass,
            exception_cls=_BeartypeCallHintPepRaiseException,
            exception_prefix=cause.exception_prefix,
        )
        # Else, this superclass is issubclassable.
    # In either case, this superclass is now issubclassable.

    # Output cause to be returned, permuted from this input cause.
    cause_return = cause.permute()

    # If this pith subclasses this superclass, set the output cause
    # justification to "None".
    if is_type_subclass(cause_return.pith, hint_superclass):
        cause_return.cause_str_or_none = None
    # Else, this pith does *NOT* subclass this superclass. In this case...
    else:
        # Description of this superclasses, defined as either...
        hint_superclass_label = (
            # If this superclass is a class, a description of this class;
            label_type(hint_superclass)
            if isinstance(hint_superclass, type) else
            # Else, this superclass is a tuple of classes. In this case, a
            # description of these classes...
            join_delimited_disjunction_types(hint_superclass)
        )

        # Human-readable string describing this failure.
        cause_return.cause_str_or_none = (
            f'{represent_pith(cause_return.pith)} not subclass of '
            f'{hint_superclass_label}'
        )

    # Return this cause.
    return cause_return
