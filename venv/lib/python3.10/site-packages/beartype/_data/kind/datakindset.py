#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **set singletons** (i.e., sets and frozen sets commonly required
throughout this codebase, reducing space and time consumption by preallocating
widely used set-centric objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Any,
    FrozenSet,
)

# ....................{ SETS                               }....................
# Note that this exact type annotation is required to avoid mypy complaints. :O
FROZENSET_EMPTY: FrozenSet[Any] = frozenset()
'''
**Empty frozen set singleton.**

Whereas Python guarantees the **empty tuple** (i.e., ``()``) to be a singleton,
Python does *not* extend that guarantee to frozen sets. This empty frozen set
singleton amends that oversight, providing efficient reuse of empty frozen sets:
e.g.,

.. code-block:: pycon

   >>> () is ()
   True  # <-- good. this is good.
   >>> frozenset() is frozenset()
   False  # <-- bad. this is bad.
   >>> from beartype._data.kind.datakindset import FROZENSET_EMPTY
   >>> FROZENSET_EMPTY is FROZENSET_EMPTY
   True  # <-- good. this is good, because we made it so.
'''
