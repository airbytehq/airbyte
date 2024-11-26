#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`604`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10

# ....................{ TESTERS                            }....................
# If the active Python interpreter targets Python >= 3.10 and thus supports PEP
# 604, define testers requiring this level of support...
if IS_PYTHON_AT_LEAST_3_10:
    # Defer version-specific imports.
    from types import UnionType  # type: ignore[attr-defined]

    #FIXME: Unit test us up.
    def is_hint_pep604(hint: object) -> bool:

        # Release the werecars, Bender!
        return isinstance(hint, UnionType)
# Else, the active Python interpreter targets Python < 3.10 and thus fails to
# support PEP 604. In this case, define fallback testers.
else:
    def is_hint_pep604(hint: object) -> bool:

        # Tonight, we howl at the moon. Tomorrow, the one-liner!
        return False


is_hint_pep604.__doc__ = (
    '''
    ``True`` only if the passed object is a :pep:`604`-compliant **union**
    (i.e., ``|``-delimited disjunction of two or more isinstanceable types).

    Parameters
    ----------
    hint : object
        Type hint to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a :pep:`604`-compliant union.
    '''
)
