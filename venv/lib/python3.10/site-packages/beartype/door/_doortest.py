#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) testers** (i.e.,
callables testing and validating :class:`beartype.door.TypeHint` instances).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDoorException

# ....................{ VALIDATORS                         }....................
def die_unless_typehint(obj: object) -> None:
    '''
    Raise an exception unless the passed object is a **type hint wrapper**
    (i.e., :class:`TypeHint` instance).

    Parameters
    ----------
    obj : object
        Arbitrary object to be validated.

    Raises
    ----------
    beartype.roar.BeartypeDoorException
        If this object is *not* a type hint wrapper.
    '''

    # Avoid circular import dependencies.
    from beartype.door._cls.doorsuper import TypeHint

    # If this object is *NOT* a type hint wrapper, raise an exception.
    if not isinstance(obj, TypeHint):
        raise BeartypeDoorException(
            f'{repr(obj)} not type hint wrapper '
            f'(i.e., "beartype.door.TypeHint" instance).'
        )
    # Else, this object is a type hint wrapper.
