#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **sign classes** (i.e., classes whose instances uniquely
identifying PEP-compliant type hints in a safe, non-deprecated manner
regardless of the Python version targeted by the active Python interpreter).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Union

# ....................{ CLASSES                            }....................
class HintSign(object):
    '''
    **Sign** (i.e., object uniquely identifying PEP-compliant type hints in a
    safe, non-deprecated manner regardless of the Python version targeted by
    the active Python interpreter).

    Attributes
    ----------
    name : str
        Uniqualified name of the :mod:`typing` attribute uniquely identified by
        this sign (e.g., ``Literal`` for :pep:`586`-compliant type hints).
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = ('name',)

    # ..................{ DUNDERS                            }..................
    def __init__(self, name: str) -> None:
        '''
        Initialize this sign.

        Parameters
        ----------
        name : str
            Uniqualified name of the :mod:`typing` attribute uniquely
            identified by this sign (e.g., ``Literal`` for :pep:`586`-compliant
            type hints).
        '''
        assert isinstance(name, str), f'{repr(name)} not string.'

        # Classify all passed parameters.
        self.name = name


    def __repr__(self) -> str:
        '''
        Machine-readable representation of this sign.
        '''

        return f"HintSign('{self.name}')"


    def __str__(self) -> str:
        '''
        Human-readable stringification of this sign.
        '''

        return f'"HintSign{self.name}"'

# ....................{ HINTS                              }....................
HintSignOrType = Union[HintSign, type]
'''
PEP-compliant type hint matching either a **sign** (i.e., object uniquely
identifying PEP-compliant type hints in a safe, non-deprecated manner
regardless of the Python version targeted by the active Python interpreter) or
**isinstanceable class** (i.e., class safely passable as the second argument to
the :func:`isinstance` builtin).
'''
