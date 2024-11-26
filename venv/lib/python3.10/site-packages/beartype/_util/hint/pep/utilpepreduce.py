#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint reducer** (i.e., callable converting a
PEP-compliant type hint satisfying various constraints into another
PEP-compliant type hint) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.hint.datahinttyping import (
    Pep484TowerComplex,
    Pep484TowerFloat,
)
from beartype._conf.confcls import BeartypeConf
from beartype._util.hint.utilhinttest import die_unless_hint

# ....................{ REDUCERS                           }....................
#FIXME: Unit test us up, please.
def reduce_hint_pep_unsigned(
    hint: object,
    conf: BeartypeConf,
    exception_prefix: str,
    *args, **kwargs
) -> object:
    '''
    Reduce the passed **unsigned PEP-compliant type hint** (i.e., type hint
    compliant with standards but identified by *no* sign, implying this hint to
    almost certainly be an isinstanceable type) if this hint satisfies various
    conditions to another (possibly signed) PEP-compliant type hint.

    Specifically:

    * If the passed configuration enables support for the :pep:`484`-compliant
      implicit numeric tower *and* this hint is:

      * The builtin :class:`float` type, this reducer expands this type to the
        ``float | int`` union of types.
      * The builtin :class:`complex` type, this reducer expands this type to the
        ``complex | float | int`` union of types.

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Final type hint to be reduced.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    All remaining passed arguments are silently ignored.

    Returns
    ----------
    object
        PEP-compliant type hint reduced from this... PEP-compliant type hint.
    '''
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'

    # If...
    if (
        # This configuration enables support for the PEP 484-compliant
        # implicit numeric tower *AND*...
        conf.is_pep484_tower and
        # This hint is either the builtin "float" or "complex" classes
        # governed by this tower...
        (hint is float or hint is complex)
    # Then expand this hint to the corresponding numeric tower.
    ):
        # Expand this hint to match...
        hint = (
            # If this hint is the builtin "float" class, both the builtin
            # "float" and "int" classes;
            Pep484TowerFloat
            if hint is float else
            # Else, this hint is the builtin "complex" class by the above
            # condition; in this case, the builtin "complex", "float", and
            # "int" classes.
            Pep484TowerComplex
        )
    # Else, this hint is truly unidentifiable.
    else:
        # If this hint is *NOT* a valid type hint, raise an exception.
        #
        # Note this function call is effectively memoized and thus fast.
        die_unless_hint(hint=hint, exception_prefix=exception_prefix)
        # Else, this hint is a valid type hint.

    # Return this hint as is unmodified.
    return hint
