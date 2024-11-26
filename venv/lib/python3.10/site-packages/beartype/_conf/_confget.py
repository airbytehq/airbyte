#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **configuration class getters** (i.e., low-level utility functions
returning various objects of interest, intended to be internally called by
various methods of the high-level :class:`beartype.BeartypeConf` class).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeConfShellVarException
from beartype.roar._roarwarn import BeartypeConfShellVarWarning
from beartype._data.func.datafuncarg import ARG_VALUE_UNPASSED
from beartype._data.hint.datahinttyping import (
    BoolTristateUnpassable,
    BoolTristate,
)
from beartype._data.os.dataosshell import (
    SHELL_VAR_CONF_IS_COLOR_NAME,
    SHELL_VAR_CONF_IS_COLOR_VALUE_TO_OBJ,
)
from beartype._util.os.utilosshell import get_shell_var_value_or_none
from beartype._util.text.utiltextjoin import join_delimited_disjunction
from warnings import warn

# ....................{ GETTERS                            }....................
def get_is_color(is_color: BoolTristateUnpassable) -> BoolTristate:
    '''
    Final value of the ``is_color`` tri-state boolean parameter accepted by the
    :meth:`beartype.BeartypeConf.__init__` constructor, derived from the passed
    parameter originally passed to that constructor as well as the external
    ``${BEARTYPE_IS_COLOR}`` shell environment variable.

    This getter derives the value of the ``is_color`` parameter as follows:

    * If the external ``${BEARTYPE_IS_COLOR}`` environment variable is set, this
      getter:

      * If the caller also explicitly passed the ``is_color`` parameter a
        different and thus conflicting value to that environment variable, emits
        a non-fatal warning informing the caller of this conflict.
      * Returns the value of that variable coerced from a useless string to the
        corresponding native Python object (e.g., from
        ``BEARTYPE_IS_COLOR="True"`` to :data:`True`).

    * Else, this getter returns the value of the ``is_color`` parameter as is.

    Parameters
    ----------
    is_color : BoolTristateUnpassable
        Original ``is_color`` parameter passed to that constructor.

    Returns
    ----------
    BoolTristate
        Final ``is_color`` parameter to be used inside that constructor.

    Raises
    ----------
    BeartypeConfParamException
        If the original``is_color`` parameter is *not* a tri-state boolean.
    BeartypeConfShellVarException
        If the external ``${BEARTYPE_IS_COLOR}`` shell environment variable is
        set to an unrecognized string (i.e., neither ``"True"``, ``"False"``,
        nor ``"None"``).
    '''

    # String value of the external shell environment variable
    # "${BEARTYPE_IS_COLOR}" globally overriding the passed "is_color" parameter
    # if the caller set this environment variable *OR* "None" otherwise.
    is_color_shell_var_value = get_shell_var_value_or_none(
        SHELL_VAR_CONF_IS_COLOR_NAME)

    # If the caller set this environment variable...
    if is_color_shell_var_value is not None:
        # If the string value of this environment variable is unrecognized...
        if (is_color_shell_var_value not in
            SHELL_VAR_CONF_IS_COLOR_VALUE_TO_OBJ):
            # Human-readable string listing the names of all valid string values
            # of this environment variable, double-quoting each such name for
            # additional readability.
            IS_COLOR_SHELL_VAR_VALUES = join_delimited_disjunction(
                strs=SHELL_VAR_CONF_IS_COLOR_VALUE_TO_OBJ.keys(),
                is_double_quoted=True,
            )

            # Raise an exception embedding this string.
            raise BeartypeConfShellVarException(
                f'Beartype configuration environment variable '
                f'"${{{SHELL_VAR_CONF_IS_COLOR_NAME}}}" '
                f'value {repr(is_color_shell_var_value)} invalid '
                f'(i.e., neither {IS_COLOR_SHELL_VAR_VALUES}).'
            )
        # Else, the string value of this environment variable is recognized.

        # Value of the "is_color" parameter represented by this string value
        # (e.g., boolean True for the string "True"). By the above validation,
        # this value is now guaranteed to be valid.
        is_color_override = SHELL_VAR_CONF_IS_COLOR_VALUE_TO_OBJ.get(
            is_color_shell_var_value)

        # If...
        if (
            # The value of the "is_color" parameter is *NOT* that of our
            # unpassed argument placeholder, then the caller explicitly passed
            # some value for this parameter. If this is the case *AND*...
            is_color != ARG_VALUE_UNPASSED and
            # The value of this parameter differs from (and thus conflicts with)
            # the value of this environment variable...
            is_color != is_color_override
        ):
            # Warn the caller that @beartype non-fatally resolved this conflict
            # by ignoring this parameter in favour of this environment variable.
            warn(
                (
                    f'Beartype configuration parameter "is_color" '
                    f'value {repr(is_color)} ignored in favour of '
                    f'environment variable '
                    f'"${{{SHELL_VAR_CONF_IS_COLOR_NAME}}}" '
                    f'value {repr(is_color_override)}.'
                ),
                BeartypeConfShellVarWarning,
            )

        # Override the value of the passed "is_color" parameter with
        # that of this environment variable.
        is_color = is_color_override
    # Else, the caller did *NOT* set this environment variable.
    #
    # If the value of the "is_color" parameter is that of our unpassed argument
    # placeholder, then the caller did *NOT* explicitly pass some value for this
    # parameter. In this case, default this parameter to "None".
    elif is_color == ARG_VALUE_UNPASSED:
        is_color = None
    # Else, the value of the "is_color" parameter is *NOT* that of our unpassed
    # argument placeholder. In this case, the caller did explicitly passed some
    # value for this parameter. Preserve this value as is.

    # Return this boolean.
    return is_color
