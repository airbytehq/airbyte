#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable argument metadata** (i.e., global magic constants
describing arguments accepted by various functions and methods).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................

# ....................{ NAMES ~ return                     }....................
ARG_NAME_RETURN = 'return'
'''
Unique name arbitrarily assigned by Python to the key of the ``__annotations__``
dunder attribute providing the type hint annotating the return of callables.

Note that Python itself prohibits callable parameters from being named
``"return"`` and thus guarantees this name to be safe and unambiguous.
'''


ARG_NAME_RETURN_REPR = repr(ARG_NAME_RETURN)
'''
Object representation of the magic string implying a return value in various
Python objects (e.g., the ``__annotations__`` dunder dictionary of annotated
callables).
'''

# ....................{ VALUES                             }....................
ARG_VALUE_UNPASSED = 0xBABECAFE
'''
**Unpassed argument value** (i.e., arbitrary magic constant serving as the
default value of an optional parameter accepted by a callable).

This constant is intentionally defined as an arbitrary integer literal
compatible with the :pep:`586`-compatible :obj:`typing.Literal` type hint
factory, simplifying annotations for optional parameters defaulting to this
unpassed argument value: e.g.,

.. code-block:: python

   from typing import Literal

   def muh_func(muh_arg: Literal[True, False, None, ARG_VALUE_UNPASSED] = (
       ARG_VALUE_UNPASSED)) -> None: ...

Usage of this default value enables a callable to deterministically
differentiate between two otherwise indistinguishable cases in call-time
semantics:

* When a caller explicitly passes that callable that optional parameter as a
  value that is possibly :data:`None`. In this case, that value is effectively
  guaranteed to *not* be this arbitrary magic constant. Moreover, since that
  value is possibly :data:`None`, testing for :data:`None` does *not* suffice to
  decide whether the caller explicitly passed that value or not.
* When a caller does *not* explicitly pass that callable that optional
  parameter. In this case, the value of that parameter is guaranteed to be this
  arbitrary magic constant.
'''
