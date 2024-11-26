#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable globals** (i.e., global constants describing various
well-known functions and methods).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................

# ....................{ SETS                               }....................
METHOD_NAMES_DUNDER_BINARY = frozenset((
    '__add__',
    '__and__',
    '__cmp__',
    '__divmod__',
    '__div__',
    '__eq__',
    '__floordiv__',
    '__ge__',
    '__gt__',
    '__iadd__',
    '__iand__',
    '__idiv__',
    '__ifloordiv__',
    '__ilshift__',
    '__imatmul__',
    '__imod__',
    '__imul__',
    '__ior__',
    '__ipow__',
    '__irshift__',
    '__isub__',
    '__itruediv__',
    '__ixor__',
    '__le__',
    '__lshift__',
    '__lt__',
    '__matmul__',
    '__mod__',
    '__mul__',
    '__ne__',
    '__or__',
    '__pow__',
    '__radd__',
    '__rand__',
    '__rdiv__',
    '__rfloordiv__',
    '__rlshift__',
    '__rmatmul__',
    '__rmod__',
    '__rmul__',
    '__ror__',
    '__rpow__',
    '__rrshift__',
    '__rshift__',
    '__rsub__',
    '__rtruediv__',
    '__rxor__',
    '__sub__',
    '__truediv__',
    '__xor__',
))
'''
Frozen set of the unqualified names of all **binary dunder methods** (i.e.,
methods whose names are both prefixed and suffixed by ``__``, which the active
Python interpreter implicitly calls to perform binary operations on instances
whose first operands are instances of the classes declaring those methods).
'''
