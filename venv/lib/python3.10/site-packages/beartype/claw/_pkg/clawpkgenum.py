#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hook enumerations** (i.e., :class:`enum.Enum` subclasses
enumerating various kinds of divergent strategies and processes specific to
import hooks defined by the :mod:`beartype.claw` subpackage).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
# from beartype.typing import Literal
from enum import (
    Enum,
    auto as next_enum_member_value,
    unique as die_unless_enum_member_values_unique,
)

# ....................{ ENUMS                              }....................
@die_unless_enum_member_values_unique
class BeartypeClawCoverage(Enum):
    '''
    Enumeration of all kinds of **import hook coverage** (i.e., competing
    package scopes over which to apply import hooks defined by the
    :mod:`beartype.claw` subpackage, each with concomitant tradeoffs with
    respect to runtime complexity and quality assurance).

    Attributes
    ----------
    PACKAGES_ALL : EnumMemberType
        **All-packages coverage** (i.e, hooking imports into *all* packages,
        including both third-party packages *and* standard packages bundled with
        Python in the standard library). This coverage is typically applied by a
        caller calling the :func:`beartype.claw.beartype_all` import hook.
    PACKAGES_MANY : EnumMemberType
        **Many-packages coverage** (i.e, hooking imports into two or more
        explicitly specified packages). This coverage is typically applied by a
        caller calling the :func:`beartype.claw.beartype_packages` import hook.
    PACKAGES_ONE : EnumMemberType
        **One-package coverage** (i.e, hooking imports into only one explicitly
        specified package). This coverage is typically applied by a caller
        calling the :func:`beartype.claw.beartype_package` import hook.
    '''

    PACKAGES_ALL = next_enum_member_value()
    PACKAGES_MANY = next_enum_member_value()
    PACKAGES_ONE = next_enum_member_value()
