#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant generic type hint exception raisers** (i.e., functions
raising human-readable exceptions called by :mod:`beartype`-decorated callables
on the first invalid parameter or return value failing a type-check against the
PEP-compliant generic type hint annotating that parameter or return).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.hint.pep.sign.datapepsigns import HintSignGeneric
from beartype._decor.error._errorcause import ViolationCause
from beartype._decor.error._errortype import find_cause_instance_type
from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
    get_hint_pep484585_generic_type,
    iter_hint_pep484585_generic_bases_unerased_tree,
)

# ....................{ GETTERS                            }....................
def find_cause_generic(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either
    satisfies or violates the :pep:`484`- or :pep:`585`-compliant **generic**
    (i.e., type hint subclassing a combination of one or more of the
    :mod:`typing.Generic` superclass, the :mod:`typing.Protocol` superclass,
    and/or other :mod:`typing` non-class pseudo-superclasses) of that cause.

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
    assert cause.hint_sign is HintSignGeneric, (
        f'{repr(cause.hint_sign)} not generic.')
    # print(f'[find_cause_generic] cause.pith: {cause.pith}')
    # print(f'[find_cause_generic] cause.hint [pre-reduction]: {cause.hint}')

    # Origin type originating this generic, deduced by stripping all child type
    # hints subscripting this hint from this hint.
    hint_type = get_hint_pep484585_generic_type(
        hint=cause.hint, exception_prefix=cause.exception_prefix)

    # Shallow output cause to be returned, type-checking only whether this pith
    # is instance of this origin type.
    cause_shallow = cause.permute(hint=hint_type)
    cause_shallow = find_cause_instance_type(cause_shallow)
    # print(f'[find_cause_generic] cause.hint [post-reduction]: {cause.hint}')

    # If this pith is *NOT* an instance of this type, return this cause.
    if cause_shallow.cause_str_or_none is not None:
        return cause_shallow
    # Else, this pith is an instance of this type.

    # For each unignorable unerased transitive pseudo-superclass originally
    # declared as an erased superclass of this generic...
    for hint_child in iter_hint_pep484585_generic_bases_unerased_tree(
        hint=cause.hint, exception_prefix=cause.exception_prefix):
        # Deep output cause to be returned, permuted from this input cause.
        cause_deep = cause.permute(hint=hint_child).find_cause()
        # print(f'tuple pith: {pith_item}\ntuple hint child: {hint_child}')

        # If this pseudo-superclass is the cause of this failure...
        if cause_deep.cause_str_or_none is not None:
            # Human-readable string prefixing this failure with additional
            # metadata describing this pseudo-superclass.
            cause_deep.cause_str_or_none = (
                f'generic base {repr(hint_child)} '
                f'{cause_deep.cause_str_or_none}'
            )

            # Return this cause.
            return cause_deep
        # Else, this pseudo-superclass is *NOT* the cause of this failure.
        # Silently continue to the next.
        # print(f'[find_cause_generic] Ignoring satisfied base {hint_child}...')

    # Return this cause as is. This pith satisfies both this generic itself
    # *AND* all pseudo-superclasses subclassed by this generic, implying this
    # pith to deeply satisfy this hint.
    return cause
