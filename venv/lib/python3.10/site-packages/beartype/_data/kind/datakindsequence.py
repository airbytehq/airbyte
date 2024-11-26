#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **sequence singletons** (i.e., lists and tuples commonly required
throughout this codebase, reducing space and time consumption by preallocating
widely used set-centric objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Any,
    Tuple,
)

# ....................{ TUPLES                             }....................
# Note that this exact type annotation is required to avoid mypy complaints. :O
TUPLE_EMPTY: Tuple[Any, ...] = ()
'''
**Empty tuple singleton.**

Yes, we know exactly what you're thinking: "Why would anyone do this, @leycec?
Why not just directly access the empty tuple singleton as ()?" Because Python
insanely requires us to do this under Python >= 3.8 to detect empty tuples:

.. code-block:: bash

   $ python3.7
   >>> () is ()
   True   # <-- yes, this is good

   $ python3.8
   >>> () is ()
   SyntaxWarning: "is" with a literal. Did you mean "=="?  # <-- WUT
   >>> TUPLE_EMPTY = ()
   >>> TUPLE_EMPTY is TUPLE_EMPTY
   True  # <-- *FACEPALM*
'''
