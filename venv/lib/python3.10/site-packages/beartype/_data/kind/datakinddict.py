#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **mapping singletons** (i.e., dictionaries commonly required
throughout this codebase, reducing space and time consumption by preallocating
widely used dictionary-centric objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Any,
    Dict,
)

# ....................{ DICTS                              }....................
# Note that this exact type annotation is required to avoid mypy complaints. :O
DICT_EMPTY: Dict[Any, Any] = {}
'''
**Empty dictionary singleton.**

Whereas Python guarantees the **empty tuple** (i.e., ``()``) to be a singleton,
Python does *not* extend that guarantee to dictionaries. This empty dictionary
singleton amends that oversight, providing efficient reuse of empty
dictionaries: e.g.,

.. code-block::

   >>> () is ()
   True  # <-- good. this is good.
   >>> {} is {}
   False  # <-- bad. this is bad.
   >>> from beartype._data.kind.datakinddict import DICT_EMPTY
   >>> DICT_EMPTY is DICT_EMPTY
   True  # <-- good. this is good, because we made it so.
'''
