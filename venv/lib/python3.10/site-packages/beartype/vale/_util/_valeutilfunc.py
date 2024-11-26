#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype validator callable utilities** (i.e., callables performing low-level
callable-centric operations on behalf of higher-level beartype validators).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeValeSubscriptionException
from beartype.vale._util._valeutiltyping import BeartypeValidatorTester
from beartype._util.func.arg.utilfuncargtest import (
    die_unless_func_args_len_flexible_equal)

# ....................{ FORMATTERS                         }....................
def die_unless_validator_tester(
    validator_tester: BeartypeValidatorTester) -> None:
    '''
    Raise an exception unless the passed object is a **validator tester** (i.e.,
    caller-defined callable accepting a single arbitrary object and returning
    either ``True`` if that object satisfies an arbitrary constraint *or*
    ``False`` otherwise).

    Parameters
    ----------
    validator_tester : BeartypeValidatorTester
        Object to be validated.

    Raises
    ----------
    beartype.roar.BeartypeValeSubscriptionException
        If that object is either:

        * *Not* callable.
        * A C-based rather than pure-Python callable.
        * A pure-Python callable accepting two or more arguments.
    '''

    # If this validator is either uncallable, a C-based callable, *OR* a
    # pure-Python callable accepting more or less than one parameter, raise
    # an exception.
    die_unless_func_args_len_flexible_equal(
        func=validator_tester,
        func_args_len_flexible=1,
        exception_cls=BeartypeValeSubscriptionException,
    )
    # Else, this validator is a pure-Python callable accepting exactly one
    # parameter. Since no further validation can be performed on this
    # callable without unsafely calling that callable, we accept this
    # callable as is for now.
    #
    # Note that we *COULD* technically inspect annotations if defined on
    # this callable as well. Since this callable is typically defined as a
    # lambda, annotations are typically *NOT* defined on this callable.
