#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **shell singletons** (i.e., magic constants pertaining to the
parent shell encapsulating the active Python interpreter, including the names of
:mod:`beartype`-specific environment variables officially recognized by
:mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Dict,
    Optional,
)

# ....................{ VARS ~ conf                        }....................
# @beartype-specific environment variables configuring beartype configurations
# (i.e., "beartype.BeartypeConf" instances).

SHELL_VAR_CONF_IS_COLOR_NAME = 'BEARTYPE_IS_COLOR'
'''
Name of the **color configuration environment variable** (i.e.,
:mod:`beartype`-specific environment variable officially recognized by
:mod:`beartype` as globally configuring the value of the
:attr:`beartype.BeartypeConf.is_color` tri-state boolean).
'''


SHELL_VAR_CONF_IS_COLOR_VALUE_TO_OBJ: Dict[str, Optional[bool]] = {
    'True': True,
    'False': False,
    'None': None,
}
'''
Dictionary mapping from each permissible string value for the **color
configuration environment variable** (i.e., whose name is
:data:`.CONF_IS_COLOR_NAME`) to the corresponding value of the
:attr:`beartype.BeartypeConf.is_color` tri-state boolean.
'''
