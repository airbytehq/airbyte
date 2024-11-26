#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`586`-compliant **type hint violation describers** (i.e.,
functions returning human-readable strings explaining violations of
:pep:`586`-compliant :attr:`typing.Literal` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._decor.error._errorcause import ViolationCause
from beartype._data.hint.pep.sign.datapepsigns import HintSignLiteral
from beartype._util.hint.pep.proposal.utilpep586 import (
    get_hint_pep586_literals)
from beartype._util.text.utiltextjoin import join_delimited_disjunction
from beartype._decor.error._util.errorutiltext import represent_pith

# ....................{ GETTERS                            }....................
def find_cause_literal(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either
    satisfies or violates the :pep:`586`-compliant :mod:`beartype`-specific
    **literal** (i.e., :attr:`typing.Literal` type hint) of that cause.

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
    assert cause.hint_sign is HintSignLiteral, (
        f'{repr(cause.hint_sign)} not "HintSignLiteral".')

    # Tuple of zero or more literal objects subscripting this hint,
    # intentionally replacing the current such tuple due to the non-standard
    # implementation of the third-party "typing_extensions.Literal" factory.
    hint_childs = get_hint_pep586_literals(
        hint=cause.hint, exception_prefix=cause.exception_prefix)

    # If this pith is equal to any literal object subscripting this hint, this
    # pith satisfies this hint. Specifically, if there exists at least one...
    if any(
        # Literal object subscripting this hint such that...
        (
            # This pith is of the same type as that of this literal *AND*...
            #
            # Note that PEP 586 explicitly requires this pith to be validated
            # to be an instance of the same type as this literal *BEFORE*
            # validated as equal to this literal, due to subtle edge cases in
            # equality comparison that could yield false positives.
            isinstance(cause.pith, type(hint_literal)) and
            # This pith is equal to this literal.
            cause.pith == hint_literal
        )
        # For each literal object subscripting this hint...
        for hint_literal in hint_childs
    ):
        # Then return this cause unmodified, as this pith deeply satisfies this
        # hint.
        return cause
    # Else, this pith fails to satisfy this hint.

    # Tuple union of the types of all literals subscripting this hint.
    hint_literal_types = tuple(
        type(hint_literal) for hint_literal in hint_childs)

    # Shallow output cause to be returned, type-checking only whether this pith
    # is an instance of one or more of these types.
    cause_shallow = cause.permute(hint=hint_literal_types).find_cause()

    # If this pith is *NOT* such an instance, return this string.
    if cause_shallow.cause_str_or_none is not None:
        return cause_shallow
    # Else, this pith is such an instance and thus shallowly satisfies this
    # hint. Since this pith fails to satisfy this hint, this pith must by
    # deduction be unequal to all literals subscripting this hint.

    # Human-readable comma-delimited disjunction of the machine-readable
    # representations of all literal objects subscripting this hint.
    cause_literals_unsatisfied = join_delimited_disjunction(
        repr(hint_literal) for hint_literal in hint_childs)

    # Deep output cause to be returned, permuted from this input cause such that
    # the justification is a human-readable string describing this failure.
    cause_deep = cause.permute(cause_str_or_none=(
        f'{represent_pith(cause.pith)} != {cause_literals_unsatisfied}.'))

    # Return this cause.
    return cause_deep
