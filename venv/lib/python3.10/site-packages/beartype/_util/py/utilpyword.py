#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Python word size** (i.e., bit length of Python variables of internal
type ``Py_ssize_t`` under the active Python interpreter) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from sys import maxsize

# ....................{ INTEGERS                           }....................
SHORT_MAX_32_BIT = 1 << 32
'''
Maximum value of **32-bit Python shorts** (i.e., integer variables of internal
type ``Py_ssize_t`` under 32-bit Python interpreters roughly corresponding to
the ``long`` C type under 32-bit machines, confusingly).

This value is suitable for comparison with :attr:`sys.maxsize`, the maximum
value of such variables under the active Python interpreter.
'''

# ....................{ BOOLEANS                           }....................
IS_WORD_SIZE_64 = maxsize > SHORT_MAX_32_BIT
'''
``True`` only if the active Python interpreter is **64-bit** (i.e., was
compiled with a 64-bit toolchain into a 64-bit executable).

Equivalently, this is ``True`` only if the maximum value of Python shorts under
this interpreter is larger than the maximum value of 32-bit Python shorts.
While obtuse, this test is well-recognized by the Python community as the
best means of testing this portably. Valid but worse alternatives include:

* ``'PROCESSOR_ARCHITEW6432' in os.environ``, which depends upon optional
  environment variables and hence is clearly unreliable.
* ``platform.architecture()[0] == '64bit'``, which fails under:

  * macOS, returning ``64bit`` even when the active Python interpreter is a
    32-bit executable binary embedded in a so-called "universal binary."
'''

# ....................{ INTEGERS ~ more                    }....................
WORD_SIZE = 64 if IS_WORD_SIZE_64 else 32
'''
Bit length of **Python shorts** (i.e., integer variables of internal type
``Py_ssize_t`` roughly corresponding to the ``long`` C type, confusingly).

This integer is guaranteed to be either:

* If the active Python interpreter is 64-bit, ``64``.
* Else, ``32``.
'''
