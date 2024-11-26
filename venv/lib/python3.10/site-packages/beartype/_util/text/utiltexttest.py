#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype string testing utilities** (i.e., callables testing whether passed
strings satisfy various conditions).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................

# ....................{ TESTERS                            }....................
def is_str_float_or_int(text: str) -> bool:
    '''
    ``True`` only if the passed string is a valid machine-readable
    representation of either an integer or finite floating-point number.

    Caveats
    ----------
    This tester intentionally returns ``False`` for non-standard floating-point
    pseudo-numbers that have no finite value, including:

    * Not-a-numbers (i.e., ``float('NaN')`` values).
    * Negative infinity (i.e., ``float('-inf')`` values).
    * Positive infinity (i.e., ``float('inf')`` values).

    Parameters
    ----------
    text : str
        String to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this string is a valid machine-readable representation
        of either an integer or finite floating-point number.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # Return true only if this text represents a finite number. See also:
    #     s.lstrip('-').replace('.','',1).replace('e-','',1).replace('e','',1).isdigit()
    return text.lstrip(
        '-').replace('.','',1).replace('e-','',1).replace('e','',1).isdigit()
