#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`593`-compliant **type hint violation describers** (i.e.,
functions returning human-readable strings explaining violations of
:pep:`593`-compliant :attr:`typing.Annotated` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
from beartype._data.hint.pep.sign.datapepsigns import HintSignAnnotated
from beartype._decor.error._errorcause import ViolationCause
from beartype._decor.error._util.errorutiltext import represent_pith
from beartype._util.hint.pep.proposal.utilpep593 import (
    get_hint_pep593_metadata,
    get_hint_pep593_metahint,
)
from beartype._util.text.utiltextmagic import CODE_INDENT_1

# ....................{ GETTERS                            }....................
def find_cause_annotated(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either
    satisfies or violates the :pep:`593`-compliant :mod:`beartype`-specific
    **metahint** (i.e., type hint annotating a standard class with one or more
    :class:`beartype.vale._core._valecore.BeartypeValidator` objects, each
    produced by subscripting the :class:`beartype.vale.Is` class or a subclass
    of that class) of that cause.

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
    assert cause.hint_sign is HintSignAnnotated, (
        f'{cause.hint_sign} not "HintSignAnnotated".')

    # Defer heavyweight imports.
    from beartype.vale._core._valecore import BeartypeValidator

    # Type hint annotated by this metahint.
    metahint = get_hint_pep593_metahint(cause.hint)

    # Tuple of zero or more arbitrary objects annotating this metahint.
    hint_validators = get_hint_pep593_metadata(cause.hint)

    # Shallow output cause to be returned, type-checking only whether this pith
    # satisfies this metahint.
    cause_shallow = cause.permute(hint=metahint).find_cause()

    # If this pith fails to satisfy this metahint, return this cause as is.
    if cause_shallow.cause_str_or_none is not None:
        return cause_shallow
    # Else, this pith satisfies this metahint.

    # Deep output cause to be returned, permuted from this input cause.
    cause_deep = cause.permute()

    # For each beartype validator annotating this metahint...
    for hint_validator in hint_validators:
        # If this is *NOT* a beartype validator, raise an exception.
        #
        # Note that this object should already be a beartype validator, as the
        # @beartype decorator enforces this constraint at decoration time.
        if not isinstance(hint_validator, BeartypeValidator):
            raise _BeartypeCallHintPepRaiseException(
                f'{cause_deep.exception_prefix}PEP 593 type hint '
                f'{repr(cause_deep.hint)} argument {repr(hint_validator)} '
                f'not beartype validator '
                f'(i.e., "beartype.vale.Is*[...]" object).'
            )
        # Else, this is a beartype validator.
        #
        # If this pith fails to satisfy this validator and is thus the cause of
        # this failure...
        elif not hint_validator.is_valid(cause_deep.pith):
            #FIXME: Unit test this up, please.
            # Human-readable string diagnosing this failure.
            hint_diagnosis = hint_validator.get_diagnosis(
                obj=cause_deep.pith,
                indent_level_outer=CODE_INDENT_1,
                indent_level_inner='',
            )

            # Human-readable string describing this failure.
            cause_deep.cause_str_or_none = (
                f'{represent_pith(cause_deep.pith)} violates validator '
                f'{repr(hint_validator)}:\n'
                f'{hint_diagnosis}'
            )

            # Immediately halt iteration.
            break
        # Else, this pith satisfies this validator. Ergo, this validator is
        # *NOT* the cause of this failure. Silently continue to the next.

    # Return this output cause.
    return cause_deep
