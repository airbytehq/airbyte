#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) type hints** (i.e.,
PEP-compliant widely used throughout the :mod:`beartype.door` subpackage).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: This submodule intentionally does *not* import the
# @beartype.beartype decorator. Why? Because that decorator conditionally
# reduces to a noop under certain contexts (e.g., `python3 -O` optimization),
# whereas the API defined by this submodule is expected to unconditionally
# operate as expected regardless of the current context.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.typing import (
    Callable,
    TypeVar,
)

# ....................{ PRIVATE ~ hints                    }....................
T = TypeVar('T')
'''
PEP-compliant type hint matching an arbitrary PEP-compliant type hint.
'''


BeartypeTypeChecker = Callable[[object], None]
'''
PEP-compliant type hint matching a **runtime type-checker** (i.e., function
created and returned by the :func:`_get_type_checker` getter, raising a
:exc:`BeartypeCallHintReturnViolation` exception when the object passed to that
function violates a PEP-compliant type hint).
'''
