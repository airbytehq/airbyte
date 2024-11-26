#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`557`-compliant **testers** (i.e., low-level callables testing
various properties of dataclasses standardized by :pep:`557`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from dataclasses import is_dataclass

# ....................{ TESTERS                           }....................
def is_type_pep557(cls: type) -> bool:
    '''
    :data:`True` only if the passed class is a **dataclass** (i.e.,
    :pep:`557`-compliant class decorated by the standard
    :func:`dataclasses.dataclass` decorator).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    cls : type
        Class to be inspected.

    Returns
    ----------
    bool
        :data:`True` only if this class is a dataclass.

    Raises
    ----------
    _BeartypeUtilTypeException
        If this object is *not* a class.
    '''

    # Avoid circular import dependencies.
    from beartype._util.cls.utilclstest import die_unless_type

    # If this object is *NOT* a type, raise an exception.
    die_unless_type(cls)
    # Else, this object is a type.

    # Return true only if this type is a dataclass.
    #
    # Note that the is_dataclass() tester was intentionally implemented
    # ambiguously to return true for both actual dataclasses *AND*
    # instances of dataclasses. Since the prior validation omits the
    # latter, this call unambiguously returns true *ONLY* if this object is
    # an actual dataclass. (Dodged a misfired bullet there, folks.)
    return is_dataclass(cls)
