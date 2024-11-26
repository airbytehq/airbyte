#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`484`-compliant :attr:`typing.NoReturn` **type hint violation
describers** (i.e., functions returning human-readable strings explaining
violations of :pep:`484`-compliant :attr:`typing.NoReturn` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.hint.pep.sign.datapepsigns import HintSignNoReturn
from beartype._decor.error._errorcause import ViolationCause
from beartype._decor.error._util.errorutiltext import represent_pith
from beartype._util.text.utiltextlabel import label_callable

# ....................{ GETTERS                            }....................
def find_cause_noreturn(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing describing the failure of the decorated callable to
    *not* return a value in violation of the :pep:`484`-compliant
    :attr:`typing.NoReturn` type hint.

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
    assert cause.hint_sign is HintSignNoReturn, (
        f'{repr(cause.hint)} not "HintSignNoReturn".')

    # Output cause to be returned, permuted from this input cause such that the
    # justification is a human-readable string describing this failure.
    cause_return = cause.permute(cause_str_or_none=(
        f'{label_callable(cause.func)} with PEP 484 return type hint '
        f'"typing.NoReturn" returned {represent_pith(cause.pith)}'
    ))

    # Return this cause.
    return cause_return
