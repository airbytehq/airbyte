#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype validator text utilities** (i.e., callables performing low-level
string-centric operations on behalf of higher-level beartype validators).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeValeUtilException
from beartype.typing import Optional
from beartype._cave._cavemap import NoneTypeOr

# ....................{ FORMATTERS                         }....................
def format_diagnosis_line(
    # Mandatory parameters.
    validator_repr: str,
    indent_level_outer: str,
    indent_level_inner: str,

    # Optional parameters.
    is_obj_valid: Optional[bool] = None,
) -> str:
    '''
    Single line of a larger human-readable **validation failure diagnosis**
    (i.e., substring describing how an arbitrary object either satisfies *or*
    violates an arbitrary validator), formatted with the passed indentation
    level and boolean value.

    Parameters
    ----------
    validator_repr : str
        **Validator representation** (i.e., unformatted single line of a larger
        diagnosis report to be formatted by this function).
    indent_level_outer : str
        **Outermost indentation level** (i.e., zero or more adjacent spaces
        prefixing each line of the returned substring).
    indent_level_inner : str
        **Innermost indentation level** (i.e., zero or more adjacent spaces
        delimiting the human-readable representation of the tri-state boolean
        and validator representation in the returned substring).
    is_obj_valid : Optional[bool]
        Tri-state boolean such that:

        * If ``True``, that arbitrary object satisfies the beartype validator
          described by this specific line.
        * If ``False``, that arbitrary object violates the beartype validator
          described by this specific line.
        * If ``None``, this specific line is entirely syntactic (e.g., a
          suffixing ")" delimiter) isolated to its own discrete line for
          readability. In this case, this line does *not* describe how an
          arbitrary object either satisfies *or* violates an arbitrary
          validator.

        Defaults to ``None``.

    Returns
    ----------
    str
        This diagnosis line formatted with this indentation level.

    Raises
    ----------
    _BeartypeValeUtilException
        If ``is_obj_valid`` is *not* a **tri-state boolean** (i.e., either
        ``True``, ``False``, or ``None``).
    '''
    assert isinstance(validator_repr, str), (
        f'{repr(validator_repr)} not string.')
    assert isinstance(indent_level_outer, str), (
        f'{repr(indent_level_outer)} not string.')
    assert isinstance(indent_level_inner, str), (
        f'{repr(indent_level_inner)} not string.')

    # If "is_obj_valid" is *NOT* a tri-state boolean, raise an exception.
    #
    # Note that this condition is intentionally validated with full-blown
    # exception handling rather than a simple "assert" statement. This condition
    # was previously implemented via a simple "assert" statement, which then
    # raised a non-human-readable assertion in an end user issue. *OH, GODS!*
    if not isinstance(is_obj_valid, NoneTypeOr[bool]):
        raise _BeartypeValeUtilException(
            f'beartype.vale._valeutiltext.format_diagnosis_line() parameter '
            f'"is_obj_valid" value {repr(is_obj_valid)} '
            f'not tri-state boolean for '
            f'validator representation: {validator_repr}'
        )
    # Else, "is_obj_valid" is a tri-state boolean.

    # String representing this boolean value, padded with spaces on the left as
    # needed to produce a column-aligned line diagnosis resembling:
    #     False == (
    #      True ==     Is[lambda foo: foo.x + foo.y >= 0] &
    #     False ==     Is[lambda foo: foo.x + foo.y <= 10]
    #              )
    is_obj_valid_str = ''
    if   is_obj_valid is True:  is_obj_valid_str = ' True == '
    elif is_obj_valid is False: is_obj_valid_str = 'False == '
    else:                       is_obj_valid_str = '         '

    # Do one thing and do it well.
    return (
        f'{indent_level_outer}'
        f'{is_obj_valid_str}'
        f'{indent_level_inner}'
        f'{validator_repr}'
    )
